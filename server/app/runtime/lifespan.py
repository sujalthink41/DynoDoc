"""Application lifespan — open/close shared resources.

Configures structured logging, then builds the database engine on startup and
disposes it on shutdown. (Runs under a real ASGI server; in-process httpx tests
inject the database via dependency override instead.)
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from app.platform.observability.logging import setup_logging
from app.platform.persistence.database import build_database


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = app.state.settings
    setup_logging(settings)
    app.state.database = build_database(settings)

    if settings.llm_api_key:
        from app.platform.ai.builder import LlmModelBuilder
        from app.platform.ai.text_generator import AdkTextGenerator

        builder = (
            LlmModelBuilder()
            .provider(settings.llm_provider)
            .model(settings.llm_model)
            .api_key(settings.llm_api_key)
        )
        model = builder.build_model()
        app.state.llm_model = model  # for ADK agent pipelines (course generation)
        app.state.text_generator = AdkTextGenerator(model=model)  # for intake
        logger.bind(provider=settings.llm_provider, model=settings.llm_model).info("LLM ready")

    logger.bind(environment=settings.environment).info("application startup complete")
    try:
        yield
    finally:
        await app.state.database.engine.dispose()
        logger.info("application shutdown complete")
