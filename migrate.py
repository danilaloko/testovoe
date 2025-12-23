#!/usr/bin/env python3
"""
Скрипт для применения миграций базы данных.
Запустите этот скрипт для применения всех непримененных миграций.
"""
from app.db.connection import init_db_pool, close_db_pool
from app.db.migrations import run_migrations, get_migration_status

if __name__ == "__main__":
    print("=" * 50)
    print("Система миграций базы данных")
    print("=" * 50)
    
    # Инициализируем пул соединений
    init_db_pool()
    
    try:
        # Показываем текущий статус
        status = get_migration_status()
        print(f"\nСтатус миграций:")
        print(f"  Всего миграций: {status['total']}")
        print(f"  Применено: {status['applied_count']}")
        print(f"  Ожидают применения: {len(status['pending'])}")
        
        if status['pending']:
            print(f"\nОжидающие миграции: {', '.join(status['pending'])}")
        
        print("\n" + "-" * 50)
        
        # Применяем миграции
        run_migrations()
        
        print("\n" + "=" * 50)
        print("Миграции завершены!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\nОшибка: {e}")
        exit(1)
    finally:
        close_db_pool()

