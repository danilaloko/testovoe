from fastapi import APIRouter
from app.api import upload, students

router = APIRouter()

router.include_router(upload.router, tags=["upload"])
router.include_router(students.router, prefix="/students", tags=["students"])

