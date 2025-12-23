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
# Отредактируйте .env файл с вашими настройками БД
```

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

## API Endpoints

### POST /upload-grades
Загрузка CSV-файла с успеваемостью студентов.

**Формат CSV:**
```csv
full_name,subject,grade
Иванов Иван Иванович,Математика,5
Петров Пётр Петрович,Физика,2
```

**Ответ:**
```json
{
  "status": "ok",
  "records_loaded": 2000,
  "students": 40
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

## Особенности

- Используется только SQL (без ORM)
- Система миграций для управления схемой БД
- Валидация входных данных
- Пул соединений с БД для оптимизации
- Обработка ошибок
- Индексы для оптимизации запросов

