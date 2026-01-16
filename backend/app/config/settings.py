from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/dbname"
    REDIS_URL: str = "redis://localhost:6379/0"
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Molecule Manager API"
    SECRET_KEY: str = "secret-key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    MAX_MOLECULE_SIZE: int = 1000
    
    class Config:
        env_file = ".env"


settings = Settings()