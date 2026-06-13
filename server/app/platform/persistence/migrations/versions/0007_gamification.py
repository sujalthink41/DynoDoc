"""create gamification tables (coins, streak, arcade plays, lesson unlocks)

Revision ID: 0007_gamification
Revises: 0006_quiz_progress
Create Date: 2026-06-14
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0007_gamification"
down_revision: str | None = "0006_quiz_progress"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _timestamps() -> list[sa.Column]:
    return [
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    ]


def upgrade() -> None:
    op.create_table(
        "player_profiles",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("coins", sa.Integer(), nullable=False),
        sa.Column("lifetime_coins", sa.Integer(), nullable=False),
        sa.Column("current_streak", sa.Integer(), nullable=False),
        sa.Column("longest_streak", sa.Integer(), nullable=False),
        sa.Column("last_activity_date", sa.Date(), nullable=True),
        *_timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_player_profiles"),
        sa.UniqueConstraint("user_id", name="uq_player_profiles_user_id"),
    )
    op.create_index("ix_player_profiles_user_id", "player_profiles", ["user_id"])

    op.create_table(
        "coin_txns",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(length=40), nullable=False),
        sa.Column("ref", sa.String(length=200), nullable=True),
        *_timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_coin_txns"),
    )
    op.create_index("ix_coin_txns_user_id", "coin_txns", ["user_id"])

    op.create_table(
        "game_plays",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("game_key", sa.String(length=40), nullable=False),
        sa.Column("play_date", sa.Date(), nullable=False),
        sa.Column("solved", sa.Boolean(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("duration_seconds", sa.Integer(), nullable=False),
        sa.Column("coins_awarded", sa.Integer(), nullable=False),
        *_timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_game_plays"),
        sa.UniqueConstraint("user_id", "game_key", "play_date", name="uq_gameplay_user_game_date"),
    )
    op.create_index("ix_game_plays_user_id", "game_plays", ["user_id"])
    op.create_index("ix_game_plays_game_key", "game_plays", ["game_key"])
    op.create_index("ix_game_plays_play_date", "game_plays", ["play_date"])

    op.create_table(
        "lesson_unlocks",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("lecture_id", sa.Uuid(), nullable=False),
        sa.Column("topic_index", sa.Integer(), nullable=False),
        *_timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_lesson_unlocks"),
        sa.ForeignKeyConstraint(
            ["lecture_id"],
            ["lectures.id"],
            name="fk_lesson_unlocks_lecture_id_lectures",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("user_id", "lecture_id", "topic_index", name="uq_unlock_user_lesson"),
    )
    op.create_index("ix_lesson_unlocks_user_id", "lesson_unlocks", ["user_id"])
    op.create_index("ix_lesson_unlocks_lecture_id", "lesson_unlocks", ["lecture_id"])


def downgrade() -> None:
    op.drop_index("ix_lesson_unlocks_lecture_id", table_name="lesson_unlocks")
    op.drop_index("ix_lesson_unlocks_user_id", table_name="lesson_unlocks")
    op.drop_table("lesson_unlocks")
    op.drop_index("ix_game_plays_play_date", table_name="game_plays")
    op.drop_index("ix_game_plays_game_key", table_name="game_plays")
    op.drop_index("ix_game_plays_user_id", table_name="game_plays")
    op.drop_table("game_plays")
    op.drop_index("ix_coin_txns_user_id", table_name="coin_txns")
    op.drop_table("coin_txns")
    op.drop_index("ix_player_profiles_user_id", table_name="player_profiles")
    op.drop_table("player_profiles")
