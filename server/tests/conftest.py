"""Shared test fixtures.

The `client` fixture drives the real ASGI app in-process via httpx — no network,
no running server — which is what makes our e2e tests fast and deterministic.
"""

from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient

from app.runtime.application import create_app
from app.runtime.settings import Settings


@pytest.fixture
def settings() -> Settings:
    return Settings(environment="test", debug=True)


@pytest.fixture
async def client(settings: Settings) -> AsyncIterator[AsyncClient]:
    app = create_app(settings)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
