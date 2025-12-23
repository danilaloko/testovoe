# Student Grades API

REST-сервис на FastAPI для загрузки и анализа успеваемости студентов.

## Требования

- Python 3.8+
- PostgreSQL 12+

## Установка

1. Клонируйте репозиторий или создайте проект

2. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
# или
venv\Scripts\activate  # для Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Установите и настройте PostgreSQL:

**Вариант А: Установка PostgreSQL сервера локально**
```bash
# Установка PostgreSQL сервера
sudo apt install -y postgresql postgresql-contrib

# Запуск сервиса
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Создание базы данных (от имени пользователя postgres)
sudo -u postgres createdb student_grades

# Или создайте пользователя и базу данных:
sudo -u postgres psql -c "CREATE USER your_user WITH PASSWORD 'your_password';"
sudo -u postgres psql -c "CREATE DATABASE student_grades OWNER your_user;"
```

**Вариант Б: Использование Docker (рекомендуется для разработки)**
```bash
# Запуск PostgreSQL через docker-compose
sudo docker-compose up -d

# Или через docker run
sudo docker run --name postgres-student-grades \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=student_grades \
  -p 5432:5432 \
  -d postgres:16

# Проверка статуса
sudo docker ps

# Остановка (когда не нужен)
sudo docker-compose down
```

**Вариант В: Подключение к удаленному серверу**
Просто настройте переменные окружения в `.env` файле с параметрами удаленного сервера.

5. Создайте базу данных (если еще не создана):
```bash
# Для локального сервера
createdb student_grades

# Или через psql
psql -U postgres -c "CREATE DATABASE student_grades;"
```

6. Настройте переменные окружения:
```bash
cp .env.example .env
# Отредактируйте .env файл с вашими настройками БД и параметрами валидации
```

**Параметры валидации CSV (опционально, есть значения по умолчанию):**
- `MAX_FILE_SIZE_MB` - максимальный размер файла в МБ (по умолчанию: 10)
- `MAX_ROWS` - максимальное количество строк (по умолчанию: 100000)
- `FULL_NAME_MIN_LENGTH` - минимальная длина ФИО (по умолчанию: 2)
- `FULL_NAME_MAX_LENGTH` - максимальная длина ФИО (по умолчанию: 255)
- `SUBJECT_MIN_LENGTH` - минимальная длина названия предмета (по умолчанию: 2)
- `SUBJECT_MAX_LENGTH` - максимальная длина названия предмета (по умолчанию: 255)
- `VALID_GRADES` - допустимые оценки через запятую (по умолчанию: 2,3,4,5)
- `BATCH_SIZE` - размер батча для вставки в БД (по умолчанию: 1000)
- `CSV_FIELD_FULL_NAME` - название поля ФИО в CSV (по умолчанию: full_name)
- `CSV_FIELD_SUBJECT` - название поля предмета в CSV (по умолчанию: subject)
- `CSV_FIELD_GRADE` - название поля оценки в CSV (по умолчанию: grade)

7. Примените миграции базы данных:
```bash
# Вариант 1: Через скрипт миграций (рекомендуется)
python migrate.py

# Вариант 2: Через скрипт инициализации
python init_db.py
```
Примечание: Миграции применяются автоматически при первом запуске приложения.

## Запуск

```bash
uvicorn app.main:app --reload
```

Сервис будет доступен по адресу: http://localhost:8000

Документация API: http://localhost:8000/docs

## Тестирование загрузки CSV

Для тестирования загрузки CSV файла можно использовать скрипт:

```bash
# Использование примера CSV файла
python scripts/upload_csv.py scripts/example_grades.csv

# Использование своего файла
python scripts/upload_csv.py path/to/your/file.csv
```

Подробнее о скриптах см. [scripts/README.md](scripts/README.md)

## API Endpoints

### POST /upload-grades
Загрузка CSV-файла с успеваемостью студентов.

**Валидация:**
- Файл должен быть в формате CSV
- Максимальный размер файла: 10 МБ
- Максимальное количество строк: 100,000
- **Обязательные поля:** `full_name`, `grade`
- **Опциональное поле:** `subject` (если указано, валидируется)
- ФИО: не пустое, минимум 2 символа, максимум 255 символов
- Предмет (если указан): минимум 2 символа, максимум 255 символов
- Оценка: целое число от 2 до 5

**Формат CSV (минимальный):**
```csv
full_name,grade
Иванов Иван Иванович,5
Петров Пётр Петрович,2
Сидоров Сидор Сидорович,4
```

**Формат CSV (с опциональным полем subject):**
```csv
full_name,subject,grade
Иванов Иван Иванович,Математика,5
Петров Пётр Петрович,Физика,2
```

**Ответ при успехе:**
```json
{
  "status": "ok",
  "records_loaded": 2000,
  "students": 40
}
```

**Ответ с предупреждениями (часть данных загружена, но есть ошибки):**
```json
{
  "status": "ok",
  "records_loaded": 1950,
  "students": 40,
  "warnings": "Обнаружено 50 ошибок при обработке",
  "error_details": ["Строка 10: оценка должна быть 2, 3, 4 или 5", ...]
}
```

### GET /students/more-than-3-twos
Возвращает студентов с более чем 3 двойками.

**Ответ:**
```json
[
  { "full_name": "Иванов Иван", "count_twos": 5 }
]
```

### GET /students/less-than-5-twos
Возвращает студентов с менее чем 5 двойками.

**Ответ:**
```json
[
  { "full_name": "Петров Пётр", "count_twos": 2 }
]
```

## Структура проекта

```
testovoe/
├── app/
│   ├── __init__.py
│   ├── main.py              # Точка входа приложения
│   ├── config.py            # Конфигурация приложения
│   ├── api/
│   │   ├── __init__.py
│   │   ├── upload.py        # Эндпоинт загрузки CSV
│   │   └── students.py      # Эндпоинты анализа студентов
│   └── db/
│       ├── __init__.py
│       ├── connection.py    # Подключение к БД
│       ├── migrations.py    # Система миграций
│       └── schema.py        # Схема БД (использует миграции)
├── migrations/              # SQL-скрипты миграций
│   ├── 000_init_schema_migrations.sql
│   └── 001_create_grades_table.sql
├── .env.example
├── .gitignore
├── docker-compose.yml   # Docker конфигурация для PostgreSQL
├── init_db.py          # Скрипт для инициализации БД
├── migrate.py          # Скрипт для применения миграций
├── requirements.txt
└── README.md
```

## Миграции базы данных

Проект использует систему миграций на основе SQL-скриптов:

- Все миграции находятся в папке `migrations/`
- Миграции применяются автоматически при старте приложения
- Можно применить миграции вручную: `python migrate.py`
- Примененные миграции отслеживаются в таблице `schema_migrations`

### Создание новой миграции

1. Создайте файл в папке `migrations/` с именем `XXX_description.sql` (где XXX - порядковый номер)
2. Напишите SQL-код для изменения схемы БД
3. Запустите `python migrate.py` для применения

Пример:
```sql
-- migrations/002_add_email_column.sql
ALTER TABLE grades ADD COLUMN email VARCHAR(255);
```

## Конфигурация

Параметры валидации CSV файлов настраиваются через переменные окружения в файле `.env`.
Все параметры имеют значения по умолчанию, поэтому настройка опциональна.

Подробнее о вариантах реализации конфигурации см. [CONFIG_OPTIONS.md](CONFIG_OPTIONS.md)

## Особенности

- Используется только SQL (без ORM)
- Система миграций для управления схемой БД
- Настраиваемая валидация входных данных через конфигурацию
- Пул соединений с БД для оптимизации
- Batch-вставка данных для производительности
- Обработка ошибок с детальной информацией
- Индексы для оптимизации запросов

