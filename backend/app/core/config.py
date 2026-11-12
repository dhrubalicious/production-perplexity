from enum import StrEnum
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    LOCAL = "local"
    TEST = "test"
    STAGING = "staging"
    PROD = "prod"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "Production Perplexity API"
    APP_ENV: Environment = Environment.LOCAL
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    ALLOWED_CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    DATABASE_URL: str = (
        "mysql+asyncmy://perplexity:perplexity_dev_pass@localhost:3306/perplexity_dev"
    )
    TEST_DATABASE_URL: str = (
        "mysql+asyncmy://perplexity:perplexity_dev_pass@localhost:3306/perplexity_test"
    )
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_RECYCLE: int = 1800
    DB_ECHO: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
