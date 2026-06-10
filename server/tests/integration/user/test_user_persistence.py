"""Integration tests for user persistence — against a real SQLite database."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.user.repository import (
    get_or_create_oauth_user,
    get_user_by_id,
    to_principal,
)
from app.shared.contracts.identity import GoogleIdentity

IDENTITY = GoogleIdentity(
    subject="google-sub-1",
    email="learner@example.com",
    name="Lina",
    picture="https://example.com/a.png",
)


async def test_first_login_creates_user(db_session: AsyncSession) -> None:
    user, is_new = await get_or_create_oauth_user(db_session, identity=IDENTITY)

    assert is_new is True
    assert user.id is not None
    assert user.email == "learner@example.com"
    assert user.google_subject == "google-sub-1"
    assert user.created_at is not None


async def test_returning_login_reuses_user(db_session: AsyncSession) -> None:
    first, _ = await get_or_create_oauth_user(db_session, identity=IDENTITY)

    updated = GoogleIdentity(subject="google-sub-1", email="new@example.com", name="Lina R.")
    second, is_new = await get_or_create_oauth_user(db_session, identity=updated)

    assert is_new is False
    assert second.id == first.id
    assert second.email == "new@example.com"  # profile refreshed from Google
    assert second.display_name == "Lina R."


async def test_get_user_by_id_and_principal(db_session: AsyncSession) -> None:
    created, _ = await get_or_create_oauth_user(db_session, identity=IDENTITY)

    fetched = await get_user_by_id(db_session, created.id)
    assert fetched is not None

    principal = to_principal(fetched)
    assert principal.id == created.id
    assert principal.subject == "google-sub-1"
    assert principal.email == "learner@example.com"
