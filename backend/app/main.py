from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from .config.settings import settings
from .src.utils.logger import app_logger
from .src.api.v1.routes import router as api_router
from .db.base import engine, Base
from .src.utils.redis_client import redis_client
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    app_logger.info("Starting application...")

    await redis_client.connect()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    app_logger.info("Database tables created")

    yield

    await redis_client.disconnect()
    app_logger.info("Shutting down application...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Molecule Management API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    redis_status = redis_client.is_connected()
    return {
        "status": "healthy",
        "redis": "connected" if redis_status else "disconnected",
    }


app.include_router(api_router, prefix=settings.API_V1_STR)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
