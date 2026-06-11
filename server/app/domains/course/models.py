"""Course-domain ORM models."""

from typing import Any
from uuid import UUID

from sqlalchemy import JSON, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.persistence.base import Base
from app.platform.persistence.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class IntakeSession(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """An in-progress (or finished) onboarding conversation for one learner."""

    __tablename__ = "intake_sessions"

    owner_user_id: Mapped[UUID] = mapped_column(Uuid, index=True)
    goal: Mapped[str] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(20), default="in_progress")
    transcript: Mapped[list[dict[str, str]]] = mapped_column(JSON, default=list)
    pending_questions: Mapped[list[str]] = mapped_column(JSON, default=list)
    profile: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
