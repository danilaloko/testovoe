from app.db.migrations import run_migrations

def create_tables():
    """
    Создание таблиц в БД через систему миграций.
    Применяет все непримененные миграции из папки migrations/
    """
    run_migrations()

