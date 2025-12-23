import psycopg2
from psycopg2 import pool
import os
from dotenv import load_dotenv

load_dotenv()

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
    try:
        connection_pool = psycopg2.pool.SimpleConnectionPool(
            1, 20, **DB_CONFIG
        )
        if connection_pool:
            print("Пул соединений с БД успешно создан")
    except (Exception, psycopg2.Error) as error:
        print(f"Ошибка при создании пула соединений: {error}")

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
        print("Пул соединений закрыт")

