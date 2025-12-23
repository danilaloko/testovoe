from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import logging
from app.db.connection import get_db_connection, return_db_connection

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/more-than-3-twos")
async def get_students_more_than_3_twos():
    """
    Возвращает ФИО студентов, у которых оценка 2 встречается больше 3 раз.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                full_name,
                COUNT(*) as count_twos
            FROM grades
            WHERE grade = 2
            GROUP BY full_name
            HAVING COUNT(*) > 3
            ORDER BY count_twos DESC, full_name
        """)
        
        results = cursor.fetchall()
        
        students = [
            {
                "full_name": row[0],
                "count_twos": row[1]
            }
            for row in results
        ]
        
        logger.info(f"Найдено студентов с более чем 3 двойками: {len(students)}")
        return JSONResponse(content=students)
        
    except Exception as e:
        logger.error(f"Ошибка при получении данных (more-than-3-twos): {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка при получении данных: {str(e)}")
    finally:
        cursor.close()
        return_db_connection(conn)

@router.get("/less-than-5-twos")
async def get_students_less_than_5_twos():
    """
    Возвращает ФИО студентов, у которых оценка 2 встречается меньше 5 раз.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Используем подзапрос для подсчета двоек у каждого студента
        cursor.execute("""
            WITH student_twos AS (
                SELECT 
                    full_name,
                    COUNT(CASE WHEN grade = 2 THEN 1 END) as count_twos
                FROM grades
                GROUP BY full_name
            )
            SELECT 
                full_name,
                count_twos
            FROM student_twos
            WHERE count_twos < 5
            ORDER BY count_twos DESC, full_name
        """)
        
        results = cursor.fetchall()
        
        students = [
            {
                "full_name": row[0],
                "count_twos": row[1]
            }
            for row in results
        ]
        
        logger.info(f"Найдено студентов с менее чем 5 двойками: {len(students)}")
        return JSONResponse(content=students)
        
    except Exception as e:
        logger.error(f"Ошибка при получении данных (less-than-5-twos): {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка при получении данных: {str(e)}")
    finally:
        cursor.close()
        return_db_connection(conn)


