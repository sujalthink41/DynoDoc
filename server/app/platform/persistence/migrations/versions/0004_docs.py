"""create docs table

Revision ID: 0004_docs
Revises: 0003_courses_lectures
Create Date: 2026-06-11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0004_docs"
down_revision: str | None = "0003_courses_lectures"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "docs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("lecture_id", sa.Uuid(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name="pk_docs"),
        sa.ForeignKeyConstraint(
            ["lecture_id"], ["lectures.id"], name="fk_docs_lecture_id_lectures", ondelete="CASCADE"
        ),
    )
    op.create_index("ix_docs_lecture_id", "docs", ["lecture_id"])


def downgrade() -> None:
    op.drop_index("ix_docs_lecture_id", table_name="docs")
    op.drop_table("docs")
