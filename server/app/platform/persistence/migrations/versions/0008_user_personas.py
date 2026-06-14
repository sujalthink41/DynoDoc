"""create user_personas table (the 'about you' questionnaire)

Revision ID: 0008_user_personas
Revises: 0007_gamification
Create Date: 2026-06-14
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0008_user_personas"
down_revision: str | None = "0007_gamification"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "user_personas",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("answers", sa.JSON(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name="pk_user_personas"),
        sa.UniqueConstraint("user_id", name="uq_user_personas_user_id"),
    )
    op.create_index("ix_user_personas_user_id", "user_personas", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_user_personas_user_id", table_name="user_personas")
    op.drop_table("user_personas")
