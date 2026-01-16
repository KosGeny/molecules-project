from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from app.config.settings import settings

Base = declarative_base()


def get_sync_database_url():
    url = settings.DATABASE_URL
    if url.startswith("postgresql+asyncpg://"):
        return url.replace("postgresql+asyncpg://", "postgresql://")
    elif url.startswith("postgresql+psycopg://"):
        return url.replace("postgresql+psycopg://", "postgresql://")
    return url


def get_sync_engine():
    return create_engine(get_sync_database_url())
