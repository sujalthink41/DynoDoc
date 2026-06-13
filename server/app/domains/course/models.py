"""Course-domain ORM models."""

from typing import Any
from uuid import UUID

from sqlalchemy import JSON, Boolean, ForeignKey, Integer, String, Text, UniqueConstraint, Uuid
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


class Course(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A generated learning roadmap for one learner."""

    __tablename__ = "courses"

    owner_user_id: Mapped[UUID] = mapped_column(Uuid, index=True)
    intake_session_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    title: Mapped[str] = mapped_column(String(300))
    goal: Mapped[str] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(20), default="ready")
    # Snapshot of the learner profile that shaped this course.
    learner_profile: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)


class Lecture(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """An ordered module within a course's roadmap."""

    __tablename__ = "lectures"

    course_id: Mapped[UUID] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"), index=True
    )
    position: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(300))
    summary: Mapped[str] = mapped_column(Text)
    topics: Mapped[list[str]] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(20), default="outlined")


class Doc(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A written lesson document within a lecture (one per topic)."""

    __tablename__ = "docs"

    lecture_id: Mapped[UUID] = mapped_column(
        ForeignKey("lectures.id", ondelete="CASCADE"), index=True
    )
    position: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(300))
    content: Mapped[str] = mapped_column(Text)


class Reference(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A curated external link (article or YouTube) for a lecture.

    Table is `lecture_references` because `references` is a reserved SQL word.
    """

    __tablename__ = "lecture_references"

    lecture_id: Mapped[UUID] = mapped_column(
        ForeignKey("lectures.id", ondelete="CASCADE"), index=True
    )
    type: Mapped[str] = mapped_column(String(20))  # "article" | "youtube"
    url: Mapped[str] = mapped_column(String(2048))
    title: Mapped[str] = mapped_column(String(500))
    position: Mapped[int] = mapped_column(Integer)


class Quiz(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """An AI-generated multiple-choice quiz for one lesson (lecture + topic)."""

    __tablename__ = "quizzes"
    __table_args__ = (
        UniqueConstraint("lecture_id", "topic_index", name="uq_quizzes_lecture_topic"),
    )

    lecture_id: Mapped[UUID] = mapped_column(
        ForeignKey("lectures.id", ondelete="CASCADE"), index=True
    )
    topic_index: Mapped[int] = mapped_column(Integer)
    # [{ "question": str, "options": [str, ...], "answer_index": int }]
    questions: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)


class LessonProgress(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A learner's progress on one lesson (lecture + topic): best quiz score + pass."""

    __tablename__ = "lesson_progress"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "lecture_id", "topic_index", name="uq_lesson_progress_user_lesson"
        ),
    )

    user_id: Mapped[UUID] = mapped_column(Uuid, index=True)
    lecture_id: Mapped[UUID] = mapped_column(
        ForeignKey("lectures.id", ondelete="CASCADE"), index=True
    )
    topic_index: Mapped[int] = mapped_column(Integer)
    best_score: Mapped[int] = mapped_column(Integer, default=0)
    passed: Mapped[bool] = mapped_column(Boolean, default=False)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
