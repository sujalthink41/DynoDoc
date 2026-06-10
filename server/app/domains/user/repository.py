"""User persistence — plain async functions over an AsyncSession.

No repository class/Protocol: we test these against a real (SQLite) database,
which is higher fidelity than an in-memory fake would be. External, non-
deterministic dependencies (Google, the LLM, the sandbox) stay behind ports —
the database does not.
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.user.dtos import Principal
from app.domains.user.models import User
from app.shared.contracts.identity import GoogleIdentity


def to_principal(user: User) -> Principal:
    return Principal(
        id=user.id,
        subject=user.google_subject,
        email=user.email,
        display_name=user.display_name,
    )


async def get_user_by_id(session: AsyncSession, user_id: UUID) -> User | None:
    return await session.get(User, user_id)


async def get_or_create_oauth_user(
    session: AsyncSession, *, identity: GoogleIdentity
) -> tuple[User, bool]:
    """Find the user for this Google identity, or create one. Returns (user, is_new).

    On a returning login we refresh the profile fields from Google (name/picture
    can change). The row is flushed so the caller has the generated id.
    """
    result = await session.execute(select(User).where(User.google_subject == identity.subject))
    user = result.scalar_one_or_none()

    if user is not None:
        user.email = identity.email
        user.display_name = identity.name
        user.avatar_url = identity.picture
        return user, False

    user = User(
        google_subject=identity.subject,
        email=identity.email,
        display_name=identity.name,
        avatar_url=identity.picture,
    )
    session.add(user)
    await session.flush()
    return user, True
