"""create courses and lectures tables

Revision ID: 0003_courses_lectures
Revises: 0002_intake_sessions
Create Date: 2026-06-11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003_courses_lectures"
down_revision: str | None = "0002_intake_sessions"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "courses",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("owner_user_id", sa.Uuid(), nullable=False),
        sa.Column("intake_session_id", sa.Uuid(), nullable=True),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("goal", sa.String(length=500), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="ready"),
        sa.Column("learner_profile", sa.JSON(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name="pk_courses"),
    )
    op.create_index("ix_courses_owner_user_id", "courses", ["owner_user_id"])

    op.create_table(
        "lectures",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("course_id", sa.Uuid(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("topics", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="outlined"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name="pk_lectures"),
        sa.ForeignKeyConstraint(
            ["course_id"], ["courses.id"], name="fk_lectures_course_id_courses", ondelete="CASCADE"
        ),
    )
    op.create_index("ix_lectures_course_id", "lectures", ["course_id"])


def downgrade() -> None:
    op.drop_index("ix_lectures_course_id", table_name="lectures")
    op.drop_table("lectures")
    op.drop_index("ix_courses_owner_user_id", table_name="courses")
    op.drop_table("courses")
