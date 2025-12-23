"""
Система миграций базы данных.
Применяет SQL-скрипты из папки migrations/ в порядке их версий.
"""
import os
from pathlib import Path
from app.db.connection import get_db_connection, return_db_connection

# Путь к папке с миграциями
MIGRATIONS_DIR = Path(__file__).parent.parent.parent / "migrations"


def init_schema_migrations():
    """Инициализация таблицы для отслеживания миграций"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Применяем нулевую миграцию для создания таблицы schema_migrations
        init_migration_file = MIGRATIONS_DIR / "000_init_schema_migrations.sql"
        if init_migration_file.exists():
            sql = init_migration_file.read_text(encoding='utf-8')
            cursor.execute(sql)
            conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при инициализации таблицы миграций: {e}")
        raise
    finally:
        cursor.close()
        return_db_connection(conn)


def get_applied_migrations():
    """Получить список примененных миграций"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT version FROM schema_migrations ORDER BY version")
        applied = {row[0] for row in cursor.fetchall()}
        return applied
    except Exception as e:
        # Если таблицы еще нет, возвращаем пустое множество
        return set()
    finally:
        cursor.close()
        return_db_connection(conn)


def get_migration_files():
    """Получить список файлов миграций в порядке версий"""
    if not MIGRATIONS_DIR.exists():
        return []
    
    migration_files = []
    for file_path in sorted(MIGRATIONS_DIR.glob("*.sql")):
        version = file_path.stem
        # Пропускаем нулевую миграцию (она применяется отдельно)
        if version != "000_init_schema_migrations":
            migration_files.append((version, file_path))
    
    return migration_files


def apply_migration(version: str, file_path: Path):
    """Применить одну миграцию"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Читаем SQL из файла
        sql = file_path.read_text(encoding='utf-8')
        
        # Выполняем SQL
        cursor.execute(sql)
        
        # Записываем информацию о примененной миграции
        cursor.execute("""
            INSERT INTO schema_migrations (version, description)
            VALUES (%s, %s)
            ON CONFLICT (version) DO NOTHING
        """, (version, f"Migration from {file_path.name}"))
        
        conn.commit()
        print(f"✓ Применена миграция: {version}")
        return True
    except Exception as e:
        conn.rollback()
        print(f"✗ Ошибка при применении миграции {version}: {e}")
        raise
    finally:
        cursor.close()
        return_db_connection(conn)


def run_migrations():
    """Применить все непримененные миграции"""
    print("Запуск системы миграций...")
    
    # Инициализируем таблицу миграций
    try:
        init_schema_migrations()
    except Exception as e:
        print(f"Предупреждение: {e}")
    
    # Получаем список примененных миграций
    applied_migrations = get_applied_migrations()
    print(f"Примененных миграций: {len(applied_migrations)}")
    
    # Получаем список файлов миграций
    migration_files = get_migration_files()
    
    if not migration_files:
        print("Миграции не найдены")
        return
    
    # Применяем новые миграции
    applied_count = 0
    for version, file_path in migration_files:
        if version not in applied_migrations:
            print(f"Применение миграции {version}...")
            apply_migration(version, file_path)
            applied_count += 1
        else:
            print(f"⊘ Миграция {version} уже применена, пропускаем")
    
    if applied_count == 0:
        print("Все миграции уже применены")
    else:
        print(f"\nПрименено новых миграций: {applied_count}")


def get_migration_status():
    """Получить статус миграций"""
    applied = get_applied_migrations()
    all_migrations = [version for version, _ in get_migration_files()]
    
    pending = [v for v in all_migrations if v not in applied]
    
    return {
        "applied": sorted(applied),
        "pending": sorted(pending),
        "total": len(all_migrations),
        "applied_count": len(applied)
    }

