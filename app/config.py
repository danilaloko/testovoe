"""
Конфигурация приложения.
Параметры можно переопределить через переменные окружения в .env файле.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class ValidationConfig:
    """Конфигурация для валидации CSV файлов"""
    
    # Размер файла (в мегабайтах, конвертируется в байты)
    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    MAX_FILE_SIZE = MAX_FILE_SIZE_MB * 1024 * 1024
    
    # Максимальное количество строк в файле
    MAX_ROWS = int(os.getenv("MAX_ROWS", "100000"))
    
    # Размер батча для вставки в БД
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", "1000"))
    
    # Валидация ФИО
    FULL_NAME_MIN_LENGTH = int(os.getenv("FULL_NAME_MIN_LENGTH", "2"))
    FULL_NAME_MAX_LENGTH = int(os.getenv("FULL_NAME_MAX_LENGTH", "255"))
    
    # Валидация предмета
    SUBJECT_MIN_LENGTH = int(os.getenv("SUBJECT_MIN_LENGTH", "2"))
    SUBJECT_MAX_LENGTH = int(os.getenv("SUBJECT_MAX_LENGTH", "255"))
    
    # Допустимые оценки (строка вида "2,3,4,5" или список)
    VALID_GRADES_STR = os.getenv("VALID_GRADES", "2,3,4,5")
    VALID_GRADES = [int(g.strip()) for g in VALID_GRADES_STR.split(",") if g.strip()]
    
    # Поддерживаемые кодировки файлов
    SUPPORTED_ENCODINGS = ["utf-8", "windows-1251"]
    
    # Названия полей CSV (можно переопределить через переменные окружения)
    CSV_FIELD_FULL_NAME = os.getenv("CSV_FIELD_FULL_NAME", "full_name")
    CSV_FIELD_SUBJECT = os.getenv("CSV_FIELD_SUBJECT", "subject")  # Опциональное поле
    CSV_FIELD_GRADE = os.getenv("CSV_FIELD_GRADE", "grade")
    
    # Получаем список обязательных полей CSV
    @classmethod
    def get_required_fields(cls):
        """Возвращает множество обязательных полей CSV (subject опциональный)"""
        return {cls.CSV_FIELD_FULL_NAME, cls.CSV_FIELD_GRADE}
    
    # Получаем список всех полей CSV (включая опциональные)
    @classmethod
    def get_all_fields(cls):
        """Возвращает множество всех полей CSV (включая опциональные)"""
        fields = {cls.CSV_FIELD_FULL_NAME, cls.CSV_FIELD_GRADE}
        if cls.CSV_FIELD_SUBJECT:
            fields.add(cls.CSV_FIELD_SUBJECT)
        return fields
    
    @classmethod
    def validate(cls):
        """Валидация конфигурации при старте приложения"""
        errors = []
        
        if cls.MAX_FILE_SIZE_MB <= 0:
            errors.append("MAX_FILE_SIZE_MB должен быть больше 0")
        
        if cls.MAX_ROWS <= 0:
            errors.append("MAX_ROWS должен быть больше 0")
        
        if cls.FULL_NAME_MIN_LENGTH < 1:
            errors.append("FULL_NAME_MIN_LENGTH должен быть >= 1")
        
        if cls.FULL_NAME_MAX_LENGTH < cls.FULL_NAME_MIN_LENGTH:
            errors.append("FULL_NAME_MAX_LENGTH должен быть >= FULL_NAME_MIN_LENGTH")
        
        if cls.SUBJECT_MIN_LENGTH < 1:
            errors.append("SUBJECT_MIN_LENGTH должен быть >= 1")
        
        if cls.SUBJECT_MAX_LENGTH < cls.SUBJECT_MIN_LENGTH:
            errors.append("SUBJECT_MAX_LENGTH должен быть >= SUBJECT_MIN_LENGTH")
        
        if not cls.VALID_GRADES:
            errors.append("VALID_GRADES должен содержать хотя бы одну оценку")
        
        # Валидация названий полей
        if not cls.CSV_FIELD_FULL_NAME or len(cls.CSV_FIELD_FULL_NAME.strip()) == 0:
            errors.append("CSV_FIELD_FULL_NAME не может быть пустым")
        
        if not cls.CSV_FIELD_GRADE or len(cls.CSV_FIELD_GRADE.strip()) == 0:
            errors.append("CSV_FIELD_GRADE не может быть пустым")
        
        # CSV_FIELD_SUBJECT опциональный, но если задан, должен быть не пустым
        if cls.CSV_FIELD_SUBJECT and len(cls.CSV_FIELD_SUBJECT.strip()) == 0:
            errors.append("CSV_FIELD_SUBJECT не может быть пустой строкой (либо не задавайте его)")
        
        # Проверка на уникальность названий полей (только обязательных)
        required_field_names = [cls.CSV_FIELD_FULL_NAME, cls.CSV_FIELD_GRADE]
        if cls.CSV_FIELD_SUBJECT:
            required_field_names.append(cls.CSV_FIELD_SUBJECT)
        
        if len(required_field_names) != len(set(required_field_names)):
            errors.append("Названия полей CSV должны быть уникальными")
        
        if errors:
            raise ValueError(f"Ошибки конфигурации валидации: {'; '.join(errors)}")
        
        return True


# Создаем экземпляр конфигурации
validation_config = ValidationConfig()

# Валидируем при импорте
validation_config.validate()

