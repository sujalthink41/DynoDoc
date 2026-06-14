"""Application configuration (12-factor: everything from the environment)."""

from functools import lru_cache
from typing import Literal

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

    # Logging: pretty colourised lines in development, structured JSON otherwise.
    log_level: str = "INFO"
    log_json: bool = False  # force JSON even in development

    # Database (asyncpg in prod, aiosqlite in tests/dev).
    database_url: str = "sqlite+aiosqlite:///./dynodoc.db"
    db_echo: bool = False

    # Signed-cookie session (Starlette SessionMiddleware) + CSRF.
    session_secret: str = "dev-only-change-me"
    csrf_header: str = "X-CSRF-Token"
    csrf_cookie: str = "dynodoc_csrf"
    # "lax" for same-origin/dev; set to "none" when the SPA and API live on
    # different domains (cross-site cookies need SameSite=None; Secure).
    session_same_site: Literal["lax", "strict", "none"] = "lax"

    # Shared secret guarding the nightly leaderboard-settlement endpoint, which a
    # scheduled job (cron) calls. Unset = endpoint disabled (503).
    settle_secret: str | None = None

    # Google OAuth (left unset until you provide them; the app degrades gracefully).
    google_client_id: str | None = None
    google_client_secret: str | None = None
    google_redirect_uri: str = "http://localhost:8000/api/v1/auth/google/callback"
    # Where to land users after a successful sign-in — the app, not the marketing page.
    frontend_post_login_url: str = "http://localhost:3000/app"

    # LLM (provider-agnostic via LiteLLM). Switching provider/model later is just
    # config. Optional until set — the app degrades to 503 on AI endpoints.
    llm_provider: str = "gemini"
    llm_model: str = "gemini-2.0-flash"
    llm_api_key: str | None = None

    # Reference curation uses free, keyless DuckDuckGo web search.
    search_max_articles: int = 4
    search_max_videos: int = 2


@lru_cache
def get_settings() -> Settings:
    """Cached settings provider. Used as a FastAPI dependency.

    In tests, override it via `app.dependency_overrides[get_settings]`.
    """
    return Settings()
