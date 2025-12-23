#!/usr/bin/env python3
"""
Скрипт для инициализации базы данных.
Применяет все миграции из папки migrations/
"""
from app.db.connection import init_db_pool, close_db_pool
from app.db.migrations import run_migrations

if __name__ == "__main__":
    print("Инициализация базы данных...")
    init_db_pool()
    try:
        run_migrations()
        print("База данных успешно инициализирована!")
    except Exception as e:
        print(f"Ошибка при инициализации: {e}")
    finally:
        close_db_pool()

