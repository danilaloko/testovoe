# Multi-stage build для оптимизации размера образа
FROM python:3.12-slim as builder

WORKDIR /app

# Установка зависимостей для сборки
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir --user -r requirements.txt

# Финальный образ
FROM python:3.12-slim

WORKDIR /app

# Установка только runtime зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Создаем непривилегированного пользователя
RUN useradd -m -u 1000 appuser

# Копируем установленные пакеты из builder stage в домашнюю директорию appuser
COPY --from=builder /root/.local /home/appuser/.local

# Добавляем путь к локальным пакетам
ENV PATH=/home/appuser/.local/bin:$PATH

# Копируем код приложения
COPY app ./app
COPY migrations ./migrations
COPY init_db.py .
COPY migrate.py .

# Меняем владельца файлов
RUN chown -R appuser:appuser /app

USER appuser

# Открываем порт
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Запуск приложения
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


