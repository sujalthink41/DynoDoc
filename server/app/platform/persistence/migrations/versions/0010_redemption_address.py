"""add shipping_address to redemptions

Revision ID: 0010_redemption_address
Revises: 0009_coin_economy
Create Date: 2026-06-14
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0010_redemption_address"
down_revision: str | None = "0009_coin_economy"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "redemptions",
        sa.Column("shipping_address", sa.String(length=600), nullable=False, server_default=""),
    )


def downgrade() -> None:
    op.drop_column("redemptions", "shipping_address")
