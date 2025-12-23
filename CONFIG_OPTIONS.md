# Варианты реализации конфигурации валидации

## Вариант 1: Переменные окружения (.env) ⭐ Простой

**Плюсы:**
- Уже используется в проекте для БД
- Простота реализации
- Легко менять без изменения кода
- Подходит для разных окружений (dev, prod)

**Минусы:**
- Все значения строковые (нужна конвертация)
- Нет типизации
- Нет валидации значений при старте

**Пример:**
```env
# .env
MAX_FILE_SIZE_MB=10
MAX_ROWS=100000
FULL_NAME_MIN_LENGTH=2
FULL_NAME_MAX_LENGTH=255
SUBJECT_MIN_LENGTH=2
SUBJECT_MAX_LENGTH=255
VALID_GRADES=2,3,4,5
```

---

## Вариант 2: Python модуль config.py ⭐ Централизованный

**Плюсы:**
- Типизация данных
- Валидация при импорте
- Легко расширять
- Можно добавить логику

**Минусы:**
- Изменения требуют правки кода
- Менее гибко для разных окружений

**Пример:**
```python
# app/config.py
class ValidationConfig:
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 МБ
    MAX_ROWS = 100000
    FULL_NAME_MIN_LENGTH = 2
    FULL_NAME_MAX_LENGTH = 255
    SUBJECT_MIN_LENGTH = 2
    SUBJECT_MAX_LENGTH = 255
    VALID_GRADES = [2, 3, 4, 5]
```

---

## Вариант 3: Комбинированный (.env + config.py) ⭐⭐ Рекомендуемый

**Плюсы:**
- Гибкость: можно менять через .env
- Дефолтные значения в коде
- Типизация и валидация
- Соответствует текущей архитектуре проекта

**Минусы:**
- Немного сложнее реализации

**Пример:**
```python
# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class ValidationConfig:
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE_MB", 10)) * 1024 * 1024
    MAX_ROWS = int(os.getenv("MAX_ROWS", 100000))
    FULL_NAME_MIN_LENGTH = int(os.getenv("FULL_NAME_MIN_LENGTH", 2))
    FULL_NAME_MAX_LENGTH = int(os.getenv("FULL_NAME_MAX_LENGTH", 255))
    # ...
```

---

## Вариант 4: Pydantic Settings ⭐⭐⭐ Современный (FastAPI best practice)

**Плюсы:**
- Официальный подход для FastAPI
- Автоматическая валидация типов
- Поддержка .env файлов
- Валидация при старте приложения

**Минусы:**
- Требует дополнительную зависимость (pydantic-settings)
- Немного сложнее для простых случаев

**Пример:**
```python
# app/config.py
from pydantic_settings import BaseSettings

class ValidationConfig(BaseSettings):
    max_file_size_mb: int = 10
    max_rows: int = 100000
    full_name_min_length: int = 2
    full_name_max_length: int = 255
    
    class Config:
        env_file = ".env"
        env_prefix = "VALIDATION_"
```

---

## Рекомендация

**Вариант 3 (Комбинированный)** - лучший выбор для текущего проекта:
- Соответствует существующей архитектуре (используется .env)
- Простой в реализации
- Гибкий для разных окружений
- Не требует дополнительных зависимостей

