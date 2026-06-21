from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Centralized application configuration. All values can be
    overridden via environment variables or a .env file — see
    .env.example for the full list with descriptions.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # ---- App metadata ----
    APP_NAME: str = "World Cup 2026 Dashboard API"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"  # development | staging | production
    DEBUG: bool = True

    # ---- Database ----
    DATABASE_URL: str = "postgresql+psycopg2://wc2026_user:wc2026_dev_password@localhost:5432/wc2026_db"

    # ---- Redis ----
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL_SECONDS: int = 30  # default cache lifetime for list endpoints
    LIVE_CACHE_TTL_SECONDS: int = 10  # shorter TTL for /live, since it changes fastest

    # ---- CORS ----
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def split_cors_origins(cls, v):
        # Allows CORS_ORIGINS to be set as a comma-separated string
        # in .env (e.g. "http://localhost:3000,https://myapp.vercel.app")
        # while still accepting a real list when set programmatically.
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # ---- Auth (for admin panel, Step 2 scope) ----
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION_this_is_a_dev_only_default_key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    ALGORITHM: str = "HS256"

    # ---- Pagination defaults ----
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # ---- External football data provider (Step 3 scope) ----
    FOOTBALL_DATA_PROVIDER: str = "mock"  # mock | api_football | sportmonks | football_data_api
    API_FOOTBALL_KEY: str = ""
    SPORTMONKS_KEY: str = ""


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance — env is read once per process."""
    return Settings()


settings = get_settings()
