"""Shared test fixtures.

The `client` fixture drives the real ASGI app in-process via httpx — no network,
no running server — which is what makes our e2e tests fast and deterministic.
"""

from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

import app.domains.course.models  # registers tables on Base.metadata
import app.domains.gamification.models  # registers tables on Base.metadata
import app.domains.user.models  # noqa: F401  (register tables on Base.metadata)
from app.entrypoints.http.deps import (
    get_database,
    get_llm_model,
    get_resource_curator,
    get_text_generator,
)
from app.platform.persistence.base import Base
from app.platform.persistence.database import Database
from app.runtime.application import create_app
from app.runtime.settings import Settings
from tests.fixtures.fakes import FakeLlm, FakeResourceCurator, FakeTextGenerator


@pytest.fixture
def settings() -> Settings:
    return Settings(environment="test", debug=True, settle_secret="test-secret")


@pytest.fixture
async def database() -> AsyncIterator[Database]:
    """A real, in-memory SQLite database with all tables created.

    StaticPool keeps the single in-memory connection alive for the test, so the
    schema + data persist and are shared between the test and the app.
    """
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield Database(engine=engine, sessionmaker=async_sessionmaker(engine, expire_on_commit=False))
    await engine.dispose()


@pytest.fixture
async def db_session(database: Database) -> AsyncIterator[AsyncSession]:
    async with database.sessionmaker() as session:
        yield session


@pytest.fixture
def fake_text_generator() -> FakeTextGenerator:
    return FakeTextGenerator()


@pytest.fixture
def fake_llm() -> FakeLlm:
    return FakeLlm()


@pytest.fixture
def fake_curator() -> FakeResourceCurator:
    return FakeResourceCurator()


@pytest.fixture
async def client(
    settings: Settings,
    database: Database,
    fake_text_generator: FakeTextGenerator,
    fake_llm: FakeLlm,
    fake_curator: FakeResourceCurator,
) -> AsyncIterator[AsyncClient]:
    app = create_app(settings)
    app.dependency_overrides[get_database] = lambda: database
    app.dependency_overrides[get_text_generator] = lambda: fake_text_generator
    app.dependency_overrides[get_llm_model] = lambda: fake_llm
    app.dependency_overrides[get_resource_curator] = lambda: fake_curator
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
