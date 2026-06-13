"""Gamification-domain ORM models: coins, streaks, arcade plays, lesson unlocks."""

from datetime import date
from uuid import UUID

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.persistence.base import Base
from app.platform.persistence.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class PlayerProfile(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A learner's gamification state: DynoCoin balance, lifetime earnings, streak."""

    __tablename__ = "player_profiles"

    user_id: Mapped[UUID] = mapped_column(Uuid, unique=True, index=True)
    coins: Mapped[int] = mapped_column(Integer, default=0)  # spendable balance
    lifetime_coins: Mapped[int] = mapped_column(
        Integer, default=0
    )  # total ever earned (leaderboard)
    current_streak: Mapped[int] = mapped_column(Integer, default=0)
    longest_streak: Mapped[int] = mapped_column(Integer, default=0)
    last_activity_date: Mapped[date | None] = mapped_column(Date, nullable=True)


class CoinTxn(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """An immutable DynoCoin ledger entry (+earn / -spend)."""

    __tablename__ = "coin_txns"

    user_id: Mapped[UUID] = mapped_column(Uuid, index=True)
    amount: Mapped[int] = mapped_column(Integer)  # positive = earned, negative = spent
    reason: Mapped[str] = mapped_column(String(40))
    ref: Mapped[str | None] = mapped_column(String(200), nullable=True)


class GamePlay(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A learner's once-per-day play of an arcade game (e.g. 'connections')."""

    __tablename__ = "game_plays"
    __table_args__ = (
        UniqueConstraint("user_id", "game_key", "play_date", name="uq_gameplay_user_game_date"),
    )

    user_id: Mapped[UUID] = mapped_column(Uuid, index=True)
    game_key: Mapped[str] = mapped_column(String(40), index=True)
    play_date: Mapped[date] = mapped_column(Date, index=True)
    solved: Mapped[bool] = mapped_column(Boolean, default=False)
    score: Mapped[int] = mapped_column(Integer, default=0)  # e.g. number of correct groups
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0)  # solve time (for speed rank)
    coins_awarded: Mapped[int] = mapped_column(Integer, default=0)


class LessonUnlock(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A coin-purchased read-unlock for one lesson (lecture + topic).

    Grants read/generate access without passing the prior quiz; the quiz still
    gates completion, the next lesson, and coin rewards.
    """

    __tablename__ = "lesson_unlocks"
    __table_args__ = (
        UniqueConstraint("user_id", "lecture_id", "topic_index", name="uq_unlock_user_lesson"),
    )

    user_id: Mapped[UUID] = mapped_column(Uuid, index=True)
    lecture_id: Mapped[UUID] = mapped_column(
        ForeignKey("lectures.id", ondelete="CASCADE"), index=True
    )
    topic_index: Mapped[int] = mapped_column(Integer)
