"""Application configuration (12-factor: everything from the environment)."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="DYNODOC_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "DynoDoc"
    version: str = "0.1.0"
    environment: str = "development"
    debug: bool = False

    api_prefix: str = "/api/v1"
    cors_origins: list[str] = ["http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    """Cached settings provider. Used as a FastAPI dependency.

    In tests, override it via `app.dependency_overrides[get_settings]`.
    """
    return Settings()
