"""Application factory — builds and configures the FastAPI app.

`create_app` takes optional Settings so tests can construct an isolated app.
A module-level `app` is exposed for `uvicorn app.runtime.application:app`.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.entrypoints.http.errors import register_exception_handlers
from app.entrypoints.http.middleware import RequestContextMiddleware
from app.entrypoints.http.routers import health
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

    # Bind these settings to the get_settings dependency for this app instance.
    app.dependency_overrides[get_settings] = lambda: settings

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestContextMiddleware)

    register_exception_handlers(app)
    wire(app, settings)

    # Infra liveness probe — intentionally unversioned (LB/k8s shouldn't depend
    # on the API version). Versioned routers mount under settings.api_prefix.
    app.include_router(health.router)

    return app


app = create_app()
