"""Reusable column groups (mixins) so models don't repeat the same boilerplate.

class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "users"
    ...
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.ids import new_uuid7


class UUIDPrimaryKeyMixin:
    """A UUID primary key, generated app-side (UUIDv7) on insert."""

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=new_uuid7)


class TimestampMixin:
    """`created_at` / `updated_at`, maintained by the database."""

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
