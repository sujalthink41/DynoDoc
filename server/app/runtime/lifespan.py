"""Application lifespan — open/close shared resources.

Builds the database engine on startup and disposes it on shutdown. (Runs under a
real ASGI server; in-process httpx tests inject the database via dependency
override instead.)
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.platform.persistence.database import build_database


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.database = build_database(app.state.settings)
    try:
        yield
    finally:
        await app.state.database.engine.dispose()
