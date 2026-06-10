"""Application lifespan — startup/shutdown hooks.

Empty for Phase 0. As slices land, this opens/closes the DB pool, the Redis
connection, and warms caches.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    # startup
    yield
    # shutdown
