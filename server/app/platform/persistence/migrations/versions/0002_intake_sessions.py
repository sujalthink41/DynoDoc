"""create intake_sessions table

Revision ID: 0002_intake_sessions
Revises: 0001_users
Create Date: 2026-06-11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002_intake_sessions"
down_revision: str | None = "0001_users"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "intake_sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("owner_user_id", sa.Uuid(), nullable=False),
        sa.Column("goal", sa.String(length=500), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="in_progress"),
        sa.Column("transcript", sa.JSON(), nullable=False),
        sa.Column("pending_questions", sa.JSON(), nullable=False),
        sa.Column("profile", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_intake_sessions"),
    )
    op.create_index("ix_intake_sessions_owner_user_id", "intake_sessions", ["owner_user_id"])


def downgrade() -> None:
    op.drop_index("ix_intake_sessions_owner_user_id", table_name="intake_sessions")
    op.drop_table("intake_sessions")
