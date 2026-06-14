"""coin economy: visit bonus + bonus course slots on profiles, redemptions table

Revision ID: 0009_coin_economy
Revises: 0008_user_personas
Create Date: 2026-06-14
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0009_coin_economy"
down_revision: str | None = "0008_user_personas"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("player_profiles", sa.Column("last_visit_date", sa.Date(), nullable=True))
    op.add_column(
        "player_profiles",
        sa.Column("bonus_course_slots", sa.Integer(), nullable=False, server_default="0"),
    )

    op.create_table(
        "redemptions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("item_key", sa.String(length=40), nullable=False),
        sa.Column("coins_spent", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name="pk_redemptions"),
    )
    op.create_index("ix_redemptions_user_id", "redemptions", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_redemptions_user_id", table_name="redemptions")
    op.drop_table("redemptions")
    op.drop_column("player_profiles", "bonus_course_slots")
    op.drop_column("player_profiles", "last_visit_date")
