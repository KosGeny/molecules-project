from fastapi import APIRouter
from .molecules import router as molecules_router

router = APIRouter()

router.include_router(molecules_router)
