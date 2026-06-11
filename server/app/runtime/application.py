"""Application factory — builds and configures the FastAPI app.

`create_app` takes optional Settings so tests can construct an isolated app.
A module-level `app` is exposed for `uvicorn app.runtime.application:app`.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.entrypoints.http.errors import register_exception_handlers
from app.entrypoints.http.middleware import RequestContextMiddleware
from app.entrypoints.http.routers import auth, courses, health, intake, users
from app.runtime.bootstrap import wire
from app.runtime.lifespan import lifespan
from app.runtime.settings import Settings, get_settings


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        lifespan=lifespan,
        docs_url="/docs",
        openapi_url="/openapi.json",
    )

    # Available to lifespan + dependencies on this app instance.
    app.state.settings = settings
    # Bind these settings to the get_settings dependency for this app instance.
    app.dependency_overrides[get_settings] = lambda: settings

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.session_secret,
        same_site="lax",
        https_only=settings.environment == "production",
    )
    app.add_middleware(RequestContextMiddleware)

    register_exception_handlers(app)
    wire(app, settings)

    # Infra liveness probe — intentionally unversioned (LB/k8s shouldn't depend
    # on the API version). Versioned routers mount under settings.api_prefix.
    app.include_router(health.router)
    app.include_router(auth.router, prefix=settings.api_prefix)
    app.include_router(users.router, prefix=settings.api_prefix)
    app.include_router(intake.router, prefix=settings.api_prefix)
    app.include_router(courses.router, prefix=settings.api_prefix)
    if settings.environment in ("development", "test"):
        app.include_router(auth.dev_router, prefix=settings.api_prefix)

    return app


app = create_app()
