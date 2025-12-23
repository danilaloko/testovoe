from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.db.connection import get_db_connection, return_db_connection

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
        
        return JSONResponse(content=students)
        
    except Exception as e:
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
        cursor.execute("""
            SELECT 
                full_name,
                COUNT(*) as count_twos
            FROM grades
            WHERE grade = 2
            GROUP BY full_name
            HAVING COUNT(*) < 5
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
        
        return JSONResponse(content=students)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении данных: {str(e)}")
    finally:
        cursor.close()
        return_db_connection(conn)

