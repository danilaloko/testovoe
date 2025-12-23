from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import csv
import io
from app.db.connection import get_db_connection, return_db_connection
from app.config import validation_config

router = APIRouter()

def validate_full_name(name: str) -> tuple[bool, str]:
    """Валидация ФИО студента"""
    if not name or len(name.strip()) == 0:
        return False, "ФИО не может быть пустым"
    if len(name) > validation_config.FULL_NAME_MAX_LENGTH:
        return False, f"ФИО не может быть длиннее {validation_config.FULL_NAME_MAX_LENGTH} символов"
    if len(name.strip()) < validation_config.FULL_NAME_MIN_LENGTH:
        return False, f"ФИО должно содержать минимум {validation_config.FULL_NAME_MIN_LENGTH} символа"
    return True, ""

def validate_grade(grade_str: str) -> tuple[bool, str, int]:
    """Валидация оценки"""
    if not grade_str or len(grade_str.strip()) == 0:
        return False, "Оценка не может быть пустой", 0
    
    try:
        grade = int(grade_str.strip())
        if grade not in validation_config.VALID_GRADES:
            valid_grades_str = ", ".join(map(str, validation_config.VALID_GRADES))
            return False, f"Оценка должна быть одной из: {valid_grades_str}", 0
        return True, "", grade
    except ValueError:
        return False, "Оценка должна быть целым числом", 0

@router.post("/upload-grades")
async def upload_grades(file: UploadFile = File(...)):
    """
    Загрузка CSV-файла с успеваемостью студентов.
    Ожидаемый формат CSV: {CSV_FIELD_FULL_NAME},{CSV_FIELD_GRADE}
    
    Валидация (параметры настраиваются через .env или app/config.py):
    - Файл должен быть в формате CSV
    - Максимальный размер файла: {MAX_FILE_SIZE_MB} МБ
    - Максимальное количество строк: {MAX_ROWS}
    - Обязательные поля: {CSV_FIELDS}
    - ФИО ({CSV_FIELD_FULL_NAME}): не пустое, минимум {FULL_NAME_MIN_LENGTH} символа, максимум {FULL_NAME_MAX_LENGTH} символов
    - Оценка ({CSV_FIELD_GRADE}): целое число из списка {VALID_GRADES}
    """.format(
        CSV_FIELD_FULL_NAME=validation_config.CSV_FIELD_FULL_NAME,
        CSV_FIELD_GRADE=validation_config.CSV_FIELD_GRADE,
        CSV_FIELDS=", ".join(sorted(validation_config.get_required_fields())),
        MAX_FILE_SIZE_MB=validation_config.MAX_FILE_SIZE_MB,
        MAX_ROWS=validation_config.MAX_ROWS,
        FULL_NAME_MIN_LENGTH=validation_config.FULL_NAME_MIN_LENGTH,
        FULL_NAME_MAX_LENGTH=validation_config.FULL_NAME_MAX_LENGTH,
        VALID_GRADES=", ".join(map(str, validation_config.VALID_GRADES))
    )
    # Проверка расширения файла
    if not file.filename or not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Файл должен быть в формате CSV")
    
    try:
        # Чтение содержимого файла
        contents = await file.read()
        
        # Проверка размера файла
        if len(contents) > validation_config.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"Размер файла превышает максимально допустимый ({validation_config.MAX_FILE_SIZE_MB} МБ)"
            )
        
        # Декодирование содержимого
        # Попытка декодировать файл в поддерживаемых кодировках
        csv_content = None
        for encoding in validation_config.SUPPORTED_ENCODINGS:
            try:
                csv_content = contents.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        
        if csv_content is None:
            encodings_str = " или ".join(validation_config.SUPPORTED_ENCODINGS)
            raise HTTPException(
                status_code=400,
                detail=f"Файл должен быть в кодировке {encodings_str}"
            )
        
        csv_reader = csv.DictReader(io.StringIO(csv_content), delimiter=';')
        
        # Валидация заголовков (используем названия полей из конфигурации)
        expected_headers = validation_config.get_required_fields()
        csv_fieldnames = set(csv_reader.fieldnames or [])
        
        if not expected_headers.issubset(csv_fieldnames):
            missing_fields = expected_headers - csv_fieldnames
            raise HTTPException(
                status_code=400,
                detail=f"CSV должен содержать обязательные заголовки: {', '.join(sorted(missing_fields))}"
            )
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        records_loaded = 0
        students_set = set()
        errors = []
        total_rows = 0
        
        try:
            # Используем batch insert для оптимизации
            batch_data = []
            
            for row_num, row in enumerate(csv_reader, start=2):  # Начинаем с 2, т.к. 1 строка - заголовки
                total_rows += 1
                
                # Проверка максимального количества строк
                if total_rows > validation_config.MAX_ROWS:
                    errors.append(f"Превышено максимальное количество строк ({validation_config.MAX_ROWS})")
                    break
                
                try:
                    # Получение значений из строки (используем названия полей из конфигурации)
                    full_name_raw = row.get(validation_config.CSV_FIELD_FULL_NAME, '').strip()
                    grade_str_raw = row.get(validation_config.CSV_FIELD_GRADE, '').strip()
                    
                    # Валидация ФИО
                    is_valid_name, name_error = validate_full_name(full_name_raw)
                    if not is_valid_name:
                        errors.append(f"Строка {row_num}: {name_error}")
                        continue
                    full_name = full_name_raw
                    
                    # Валидация оценки
                    is_valid_grade, grade_error, grade = validate_grade(grade_str_raw)
                    if not is_valid_grade:
                        errors.append(f"Строка {row_num}: {grade_error}")
                        continue
                    
                    # Добавляем в batch
                    batch_data.append((full_name, grade))
                    students_set.add(full_name)
                    
                    # Выполняем batch insert при достижении размера батча
                    if len(batch_data) >= validation_config.BATCH_SIZE:
                        cursor.executemany("""
                            INSERT INTO grades (full_name, grade)
                            VALUES (%s, %s)
                        """, batch_data)
                        records_loaded += len(batch_data)
                        batch_data = []
                    
                except KeyError as e:
                    errors.append(f"Строка {row_num}: отсутствует обязательное поле {str(e)}")
                    continue
                except Exception as e:
                    errors.append(f"Строка {row_num}: {str(e)}")
                    continue
            
            # Вставляем оставшиеся данные
            if batch_data:
                cursor.executemany("""
                    INSERT INTO grades (full_name, grade)
                    VALUES (%s, %s)
                """, batch_data)
                records_loaded += len(batch_data)
            
            conn.commit()
            
            # Если не удалось загрузить ни одной записи
            if records_loaded == 0:
                error_message = "Не удалось загрузить данные"
                if errors:
                    error_details = '; '.join(errors[:10])
                    if len(errors) > 10:
                        error_details += f" (и еще {len(errors) - 10} ошибок)"
                    error_message += f". Ошибки: {error_details}"
                raise HTTPException(status_code=400, detail=error_message)
            
            response = {
                "status": "ok",
                "records_loaded": records_loaded,
                "students": len(students_set)
            }
            
            if errors:
                response["warnings"] = f"Обнаружено {len(errors)} ошибок при обработке"
                if len(errors) <= 20:
                    response["error_details"] = errors[:20]
            
            return JSONResponse(content=response)
            
        except Exception as e:
            conn.rollback()
            raise HTTPException(status_code=500, detail=f"Ошибка при загрузке данных: {str(e)}")
        finally:
            cursor.close()
            return_db_connection(conn)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обработке файла: {str(e)}")

