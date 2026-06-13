"""create quizzes and lesson_progress tables

Revision ID: 0006_quiz_progress
Revises: 0005_references
Create Date: 2026-06-12
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0006_quiz_progress"
down_revision: str | None = "0005_references"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "quizzes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("lecture_id", sa.Uuid(), nullable=False),
        sa.Column("topic_index", sa.Integer(), nullable=False),
        sa.Column("questions", sa.JSON(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name="pk_quizzes"),
        sa.ForeignKeyConstraint(
            ["lecture_id"],
            ["lectures.id"],
            name="fk_quizzes_lecture_id_lectures",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("lecture_id", "topic_index", name="uq_quizzes_lecture_topic"),
    )
    op.create_index("ix_quizzes_lecture_id", "quizzes", ["lecture_id"])

    op.create_table(
        "lesson_progress",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("lecture_id", sa.Uuid(), nullable=False),
        sa.Column("topic_index", sa.Integer(), nullable=False),
        sa.Column("best_score", sa.Integer(), nullable=False),
        sa.Column("passed", sa.Boolean(), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name="pk_lesson_progress"),
        sa.ForeignKeyConstraint(
            ["lecture_id"],
            ["lectures.id"],
            name="fk_lesson_progress_lecture_id_lectures",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "user_id", "lecture_id", "topic_index", name="uq_lesson_progress_user_lesson"
        ),
    )
    op.create_index("ix_lesson_progress_user_id", "lesson_progress", ["user_id"])
    op.create_index("ix_lesson_progress_lecture_id", "lesson_progress", ["lecture_id"])


def downgrade() -> None:
    op.drop_index("ix_lesson_progress_lecture_id", table_name="lesson_progress")
    op.drop_index("ix_lesson_progress_user_id", table_name="lesson_progress")
    op.drop_table("lesson_progress")
    op.drop_index("ix_quizzes_lecture_id", table_name="quizzes")
    op.drop_table("quizzes")
