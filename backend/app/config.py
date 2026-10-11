from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "SkyNest Hotels API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database Configuration
    DATABASE_URL: Optional[str] = "postgresql://postgres:postgres@localhost:5432/hotel_db"

    # JWT Authentication Configuration
    JWT_SECRET_KEY: str = "skynest-super-secret-key-change-in-production-2026"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 720  # 12 hours

@lru_cache()
def get_settings() -> Settings:
    return Settings()
