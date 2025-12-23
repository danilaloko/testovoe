# Docker инструкции

## Быстрый старт

Запустить весь проект одной командой:

```bash
docker-compose up -d
```

Сервис будет доступен на http://localhost:8000


## Структура сервисов

### Сервис `app`
- **Порт**: 8000
- **Образ**: Собирается из `Dockerfile`
- **Зависимости**: PostgreSQL (ждет healthy статус)
- **Restart policy**: unless-stopped

### Сервис `postgres`
- **Порт**: 5432
- **Образ**: postgres:16
- **Volume**: postgres_data (постоянное хранилище)
- **Health check**: проверка каждые 10 секунд

## Переменные окружения

Переменные для сервиса `app` можно изменить в `docker-compose.yml`:

```yaml
environment:
  - DB_HOST=postgres          # Хост БД
  - DB_PORT=5432             # Порт БД
  - DB_NAME=student_grades   # Имя БД
  - DB_USER=postgres         # Пользователь БД
  - DB_PASSWORD=postgres     # Пароль БД
  - MAX_FILE_SIZE_MB=10      # Макс размер CSV
  - MAX_ROWS=100000          # Макс строк в CSV
  - BATCH_SIZE=1000          # Размер батча для вставки
```
