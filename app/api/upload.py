from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import csv
import io
from app.db.connection import get_db_connection, return_db_connection

router = APIRouter()

@router.post("/upload-grades")
async def upload_grades(file: UploadFile = File(...)):
    """
    Загрузка CSV-файла с успеваемостью студентов.
    Ожидаемый формат CSV: full_name,subject,grade
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Файл должен быть в формате CSV")
    
    try:
        # Чтение содержимого файла
        contents = await file.read()
        csv_content = contents.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        
        # Валидация заголовков
        expected_headers = {'full_name', 'subject', 'grade'}
        if not expected_headers.issubset(set(csv_reader.fieldnames or [])):
            raise HTTPException(
                status_code=400,
                detail=f"CSV должен содержать заголовки: {', '.join(expected_headers)}"
            )
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        records_loaded = 0
        students_set = set()
        errors = []
        
        try:
            for row_num, row in enumerate(csv_reader, start=2):  # Начинаем с 2, т.к. 1 строка - заголовки
                try:
                    # Валидация данных
                    full_name = row['full_name'].strip()
                    subject = row['subject'].strip()
                    grade_str = row['grade'].strip()
                    
                    # Проверка на пустые значения
                    if not full_name or not subject or not grade_str:
                        errors.append(f"Строка {row_num}: пустые значения не допускаются")
                        continue
                    
                    # Валидация оценки
                    try:
                        grade = int(grade_str)
                        if grade not in [2, 3, 4, 5]:
                            errors.append(f"Строка {row_num}: оценка должна быть 2, 3, 4 или 5")
                            continue
                    except ValueError:
                        errors.append(f"Строка {row_num}: оценка должна быть числом")
                        continue
                    
                    # Вставка данных в БД
                    cursor.execute("""
                        INSERT INTO grades (full_name, subject, grade)
                        VALUES (%s, %s, %s)
                    """, (full_name, subject, grade))
                    
                    records_loaded += 1
                    students_set.add(full_name)
                    
                except Exception as e:
                    errors.append(f"Строка {row_num}: {str(e)}")
                    continue
            
            conn.commit()
            
            # Если есть ошибки, но часть данных загружена
            if errors and records_loaded == 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"Не удалось загрузить данные. Ошибки: {'; '.join(errors[:10])}"
                )
            
            response = {
                "status": "ok",
                "records_loaded": records_loaded,
                "students": len(students_set)
            }
            
            if errors:
                response["warnings"] = f"Обнаружено {len(errors)} ошибок при обработке"
            
            return JSONResponse(content=response)
            
        except Exception as e:
            conn.rollback()
            raise HTTPException(status_code=500, detail=f"Ошибка при загрузке данных: {str(e)}")
        finally:
            cursor.close()
            return_db_connection(conn)
            
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Файл должен быть в кодировке UTF-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обработке файла: {str(e)}")

