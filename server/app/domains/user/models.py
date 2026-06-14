"""User ORM model. Uses the shared mixins so id/timestamps aren't re-declared."""

from uuid import UUID

from sqlalchemy import JSON, Boolean, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.persistence.base import Base
from app.platform.persistence.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("google_subject", name="uq_users_google_subject"),)

    google_subject: Mapped[str] = mapped_column(String(255), index=True)
    email: Mapped[str] = mapped_column(String(320), index=True)
    display_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class UserPersona(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Fun, optional 'about you' answers — used to personalize future features."""

    __tablename__ = "user_personas"

    user_id: Mapped[UUID] = mapped_column(Uuid, unique=True, index=True)
    # { question_key: answer } — keys defined in app/domains/user/persona.py
    answers: Mapped[dict[str, str]] = mapped_column(JSON, default=dict)
