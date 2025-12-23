import psycopg2
from psycopg2 import pool
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Параметры подключения к БД
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "student_grades"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres")
}

# Пул соединений
connection_pool = None

def init_db_pool():
    """Инициализация пула соединений с БД"""
    global connection_pool
    import time
    
    max_retries = 5
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Попытка подключения к БД (попытка {attempt + 1}/{max_retries})...")
            logger.info(f"Параметры подключения: host={DB_CONFIG['host']}, port={DB_CONFIG['port']}, db={DB_CONFIG['database']}, user={DB_CONFIG['user']}")
            
            connection_pool = psycopg2.pool.SimpleConnectionPool(
                1, 20, **DB_CONFIG
            )
            if connection_pool:
                logger.info("Пул соединений с БД успешно создан")
                return
        except (Exception, psycopg2.Error) as error:
            logger.warning(f"Ошибка при создании пула соединений (попытка {attempt + 1}/{max_retries}): {error}")
            if attempt < max_retries - 1:
                logger.info(f"Повторная попытка через {retry_delay} секунд...")
                time.sleep(retry_delay)
            else:
                logger.error(f"Не удалось подключиться к БД после {max_retries} попыток")
                raise

def get_db_connection():
    """Получение соединения из пула"""
    if connection_pool:
        return connection_pool.getconn()
    else:
        return psycopg2.connect(**DB_CONFIG)

def return_db_connection(conn):
    """Возврат соединения в пул"""
    if connection_pool:
        connection_pool.putconn(conn)
    else:
        conn.close()

def close_db_pool():
    """Закрытие пула соединений"""
    if connection_pool:
        connection_pool.closeall()
        logger.info("Пул соединений закрыт")

