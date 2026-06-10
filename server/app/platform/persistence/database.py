"""Database handle + engine/sessionmaker construction.

One async engine serves both Postgres (prod, via asyncpg) and SQLite (tests,
via aiosqlite). The `Database` dataclass is what the app holds and hands out
sessions from.
"""

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.runtime.settings import Settings


@dataclass(slots=True)
class Database:
    engine: AsyncEngine
    sessionmaker: async_sessionmaker[AsyncSession]


def build_database(settings: Settings) -> Database:
    engine = create_async_engine(settings.database_url, echo=settings.db_echo)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    return Database(engine=engine, sessionmaker=sessionmaker)
