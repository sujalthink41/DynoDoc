"""DTOs for the gamification domain (coins, streak, arcade, leaderboard)."""

from datetime import date, datetime

from pydantic import BaseModel


class PlayerView(BaseModel):
    """A learner's wallet + streak, plus whether today's game is done."""

    coins: int
    lifetime_coins: int
    current_streak: int
    longest_streak: int
    played_today: bool
    bonus_course_slots: int


class DailyBonusView(BaseModel):
    awarded: int  # coins granted by today's visit (0 if already claimed today)
    coins: int  # new balance


class RewardView(BaseModel):
    key: str
    title: str
    emoji: str
    cost: int
    claimed: bool
    affordable: bool


class RewardsView(BaseModel):
    coins: int
    rewards: list[RewardView]


class CoinTxnView(BaseModel):
    amount: int
    reason: str
    created_at: datetime


class RedemptionView(BaseModel):
    """One merch redemption in the learner's history."""

    item_key: str
    title: str
    emoji: str
    coins_spent: int
    shipping_address: str
    created_at: datetime


# --- Connections (daily grouping game) ------------------------------------


class ConnGroupView(BaseModel):
    """One answer group — revealed only in the result."""

    label: str
    level: int
    members: list[str]


class ConnectionsView(BaseModel):
    """Today's board sent to the client (no group answers)."""

    play_date: date
    tiles: list[str]
    group_count: int
    group_size: int
    difficulty: int
    difficulty_label: str
    played: bool
    solved: bool
    score: int


class ConnectionsResult(BaseModel):
    solved: bool
    correct_groups: int
    total_groups: int
    coins_awarded: int
    current_streak: int
    new_balance: int
    groups: list[ConnGroupView]  # the answer key, revealed after submitting


# --- Leaderboard ----------------------------------------------------------


class LeaderboardEntry(BaseModel):
    rank: int
    name: str
    avatar_url: str | None
    is_me: bool
    coins: int  # lifetime coins (all-time) or coins earned today (daily)
    correct: int | None = None  # daily only: groups solved today
    duration_seconds: int | None = None  # daily only: solve time


class LeaderboardView(BaseModel):
    period: str  # "all" | "today"
    top: list[LeaderboardEntry]
    me: LeaderboardEntry | None


# --- Profile & achievements -----------------------------------------------


class AchievementView(BaseModel):
    key: str
    title: str
    description: str
    icon: str
    goal: int
    current: int
    unlocked: bool


class ProfileStatsView(BaseModel):
    coins: int
    lifetime_coins: int
    current_streak: int
    longest_streak: int
    rank: int
    courses_count: int
    courses_completed: int
    lessons_passed: int
    lessons_mastered: int
    connections_played: int
    connections_solved: int
    unlocked_count: int
    total_achievements: int
    achievements: list[AchievementView]
