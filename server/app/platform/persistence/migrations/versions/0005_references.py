"""create lecture_references table

Revision ID: 0005_references
Revises: 0004_docs
Create Date: 2026-06-11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0005_references"
down_revision: str | None = "0004_docs"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "lecture_references",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("lecture_id", sa.Uuid(), nullable=False),
        sa.Column("type", sa.String(length=20), nullable=False),
        sa.Column("url", sa.String(length=2048), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name="pk_lecture_references"),
        sa.ForeignKeyConstraint(
            ["lecture_id"],
            ["lectures.id"],
            name="fk_lecture_references_lecture_id_lectures",
            ondelete="CASCADE",
        ),
    )
    op.create_index("ix_lecture_references_lecture_id", "lecture_references", ["lecture_id"])


def downgrade() -> None:
    op.drop_index("ix_lecture_references_lecture_id", table_name="lecture_references")
    op.drop_table("lecture_references")
