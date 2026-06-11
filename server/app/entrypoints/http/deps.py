"""Shared HTTP dependencies: DB session (unit-of-work per request) + current user."""

from collections.abc import AsyncIterator
from typing import cast

from fastapi import Depends, Request
from google.adk.models.base_llm import BaseLlm
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.user.models import User
from app.domains.user.repository import get_user_by_id
from app.platform.auth.session import read_session
from app.platform.persistence.database import Database
from app.shared.contracts.llm import TextGenerator
from app.shared.errors import DependencyUnavailableError, UnauthorizedError


def get_database(request: Request) -> Database:
    return cast(Database, request.app.state.database)


def get_text_generator(request: Request) -> TextGenerator:
    generator = getattr(request.app.state, "text_generator", None)
    if generator is None:
        raise DependencyUnavailableError("LLM is not configured", code="llm_unavailable")
    return cast(TextGenerator, generator)


def get_llm_model(request: Request) -> BaseLlm:
    """The raw LLM model for ADK agent pipelines (course generation)."""
    model = getattr(request.app.state, "llm_model", None)
    if model is None:
        raise DependencyUnavailableError("LLM is not configured", code="llm_unavailable")
    return cast(BaseLlm, model)


async def db_session(
    db: Database = Depends(get_database),
) -> AsyncIterator[AsyncSession]:
    """One transaction per request: commit on success, roll back on error."""
    async with db.sessionmaker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def require_principal(
    request: Request,
    session: AsyncSession = Depends(db_session),
) -> User:
    """Resolve the logged-in user from the session cookie, or 401."""
    data = read_session(request.session)
    if data is None:
        raise UnauthorizedError("Not authenticated")
    user = await get_user_by_id(session, data.principal.id)
    if user is None or not user.is_active:
        raise UnauthorizedError("Not authenticated")
    return user
