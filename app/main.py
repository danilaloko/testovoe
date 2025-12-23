from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api import router
from app.db.connection import init_db_pool, close_db_pool
from app.db.migrations import run_migrations
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Startup
    logger.info("Запуск приложения Student Grades API")
    init_db_pool()
    # Применяем миграции при старте приложения
    run_migrations()
    logger.info("Приложение успешно запущено")
    
    yield
    
    # Shutdown
    logger.info("Остановка приложения")
    close_db_pool()
    logger.info("Приложение остановлено")


app = FastAPI(
    title="Student Grades API",
    description="REST-сервис для загрузки и анализа успеваемости студентов",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router)


@app.get("/")
async def root():
    return {"message": "Student Grades API"}


@app.get("/health")
async def health():
    """Health check endpoint для мониторинга"""
    return {"status": "healthy"}

