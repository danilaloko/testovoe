from fastapi import FastAPI
from app.api import router
from app.db.connection import init_db_pool, close_db_pool
from app.db.migrations import run_migrations

app = FastAPI(
    title="Student Grades API",
    description="REST-сервис для загрузки и анализа успеваемости студентов",
    version="1.0.0"
)

app.include_router(router)

@app.on_event("startup")
async def startup_event():
    """Инициализация при старте приложения"""
    init_db_pool()
    # Применяем миграции при старте приложения
    run_migrations()

@app.on_event("shutdown")
async def shutdown_event():
    """Закрытие соединений при остановке приложения"""
    close_db_pool()

@app.get("/")
async def root():
    return {"message": "Student Grades API"}

