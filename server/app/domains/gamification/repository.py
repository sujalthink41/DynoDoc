"""Gamification persistence + coin/streak rules (plain async functions)."""

from datetime import date, timedelta
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.course.models import Lecture
from app.domains.gamification.dtos import CoinTxnView, PlayerView
from app.domains.gamification.models import (
    CoinTxn,
    GamePlay,
    LessonUnlock,
    PlayerProfile,
    Redemption,
)
from app.domains.user.models import User
from app.shared.errors import AppError

# --- DynoCoin economy (tunable in one place) ------------------------------
CONNECTIONS_REWARD = 10  # solving the daily game (0 if not fully solved)
DAILY_VISIT_REWARD = 2  # first visit each day
LESSON_COMPLETE_REWARD = 5  # passing a lesson's quiz (first time)
COURSE_COMPLETE_REWARD = 100  # finishing a whole course (first time)
UNLOCK_COST = 100  # spend to read-unlock a locked lesson
EXTRA_COURSE_COST = 500  # spend to earn one extra course slot beyond the free limit


async def get_or_create_profile(session: AsyncSession, user_id: UUID) -> PlayerProfile:
    result = await session.execute(select(PlayerProfile).where(PlayerProfile.user_id == user_id))
    profile = result.scalar_one_or_none()
    if profile is None:
        profile = PlayerProfile(user_id=user_id)
        session.add(profile)
        await session.flush()
    return profile


async def award_coins(
    session: AsyncSession, *, user_id: UUID, amount: int, reason: str, ref: str | None = None
) -> PlayerProfile:
    """Add coins (amount > 0) to the balance + lifetime total, and record a ledger entry."""
    profile = await get_or_create_profile(session, user_id)
    profile.coins += amount
    profile.lifetime_coins += amount
    session.add(CoinTxn(user_id=user_id, amount=amount, reason=reason, ref=ref))
    await session.flush()
    return profile


async def spend_coins(
    session: AsyncSession, *, user_id: UUID, amount: int, reason: str, ref: str | None = None
) -> PlayerProfile:
    """Deduct from the spendable balance (lifetime is unaffected), or raise 402."""
    profile = await get_or_create_profile(session, user_id)
    if profile.coins < amount:
        raise AppError("Not enough DynoCoins", code="insufficient_coins", status_code=402)
    profile.coins -= amount
    session.add(CoinTxn(user_id=user_id, amount=-amount, reason=reason, ref=ref))
    await session.flush()
    return profile


def bump_streak(profile: PlayerProfile, today: date) -> None:
    """Advance the daily streak for an activity on `today` (no coin payout)."""
    last = profile.last_activity_date
    if last == today:
        return  # already counted today
    if last == today - timedelta(days=1):
        profile.current_streak += 1
    else:
        profile.current_streak = 1
    profile.last_activity_date = today
    profile.longest_streak = max(profile.longest_streak, profile.current_streak)


async def daily_visit_bonus(session: AsyncSession, user_id: UUID, today: date) -> int:
    """Award the once-a-day visit bonus; returns coins granted (0 if already today)."""
    profile = await get_or_create_profile(session, user_id)
    if profile.last_visit_date == today:
        return 0
    profile.last_visit_date = today
    await award_coins(session, user_id=user_id, amount=DAILY_VISIT_REWARD, reason="daily_visit")
    return DAILY_VISIT_REWARD


async def list_redemptions(session: AsyncSession, user_id: UUID) -> list[Redemption]:
    result = await session.execute(select(Redemption).where(Redemption.user_id == user_id))
    return list(result.scalars().all())


async def redeem_reward(
    session: AsyncSession, *, user_id: UUID, item_key: str, cost: int, address: str
) -> PlayerProfile:
    """Spend coins on a merch reward (deducts the balance) and record it + address."""
    profile = await spend_coins(session, user_id=user_id, amount=cost, reason=f"reward:{item_key}")
    session.add(
        Redemption(user_id=user_id, item_key=item_key, coins_spent=cost, shipping_address=address)
    )
    await session.flush()
    return profile


async def buy_course_slot(session: AsyncSession, *, user_id: UUID, cost: int) -> PlayerProfile:
    """Spend coins for one extra course slot beyond the free limit."""
    profile = await spend_coins(session, user_id=user_id, amount=cost, reason="extra_course")
    profile.bonus_course_slots += 1
    await session.flush()
    return profile


async def list_recent_txns(session: AsyncSession, user_id: UUID, limit: int = 10) -> list[CoinTxn]:
    result = await session.execute(
        select(CoinTxn)
        .where(CoinTxn.user_id == user_id)
        .order_by(CoinTxn.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


# --- Arcade plays (once per day per game) ---------------------------------


async def get_play(
    session: AsyncSession, user_id: UUID, game_key: str, day: date
) -> GamePlay | None:
    result = await session.execute(
        select(GamePlay).where(
            GamePlay.user_id == user_id,
            GamePlay.game_key == game_key,
            GamePlay.play_date == day,
        )
    )
    return result.scalar_one_or_none()


async def game_play_counts(session: AsyncSession, user_id: UUID, game_key: str) -> tuple[int, int]:
    """(total plays, solved plays) for a learner in one game — for profile stats."""
    total = await session.execute(
        select(func.count())
        .select_from(GamePlay)
        .where(GamePlay.user_id == user_id, GamePlay.game_key == game_key)
    )
    solved = await session.execute(
        select(func.count())
        .select_from(GamePlay)
        .where(
            GamePlay.user_id == user_id,
            GamePlay.game_key == game_key,
            GamePlay.solved.is_(True),
        )
    )
    return int(total.scalar_one()), int(solved.scalar_one())


async def add_play(
    session: AsyncSession,
    *,
    user_id: UUID,
    game_key: str,
    day: date,
    solved: bool,
    score: int,
    duration_seconds: int,
    coins_awarded: int,
) -> GamePlay:
    play = GamePlay(
        user_id=user_id,
        game_key=game_key,
        play_date=day,
        solved=solved,
        score=score,
        duration_seconds=duration_seconds,
        coins_awarded=coins_awarded,
    )
    session.add(play)
    await session.flush()
    return play


# --- Leaderboard (ranked by lifetime coins earned) ------------------------


async def leaderboard_top(
    session: AsyncSession, limit: int = 20
) -> list[tuple[PlayerProfile, User]]:
    result = await session.execute(
        select(PlayerProfile, User)
        .join(User, User.id == PlayerProfile.user_id)
        .order_by(PlayerProfile.lifetime_coins.desc(), PlayerProfile.created_at.asc())
        .limit(limit)
    )
    return [(row[0], row[1]) for row in result.all()]


async def player_rank(session: AsyncSession, lifetime_coins: int) -> int:
    result = await session.execute(
        select(func.count())
        .select_from(PlayerProfile)
        .where(PlayerProfile.lifetime_coins > lifetime_coins)
    )
    return int(result.scalar_one()) + 1


async def daily_leaderboard(
    session: AsyncSession, game_key: str, day: date, limit: int = 20
) -> list[tuple[GamePlay, User]]:
    """Today's plays ranked by most groups solved, then fastest."""
    result = await session.execute(
        select(GamePlay, User)
        .join(User, User.id == GamePlay.user_id)
        .where(GamePlay.game_key == game_key, GamePlay.play_date == day)
        .order_by(GamePlay.score.desc(), GamePlay.duration_seconds.asc())
        .limit(limit)
    )
    return [(row[0], row[1]) for row in result.all()]


async def daily_play_rank(
    session: AsyncSession, game_key: str, day: date, score: int, duration_seconds: int
) -> int:
    """Rank of a (score, time) play among today's plays — higher score, then faster, wins."""
    result = await session.execute(
        select(func.count())
        .select_from(GamePlay)
        .where(
            GamePlay.game_key == game_key,
            GamePlay.play_date == day,
            (GamePlay.score > score)
            | ((GamePlay.score == score) & (GamePlay.duration_seconds < duration_seconds)),
        )
    )
    return int(result.scalar_one()) + 1


# --- Lesson unlocks -------------------------------------------------------


async def get_lesson_unlock(
    session: AsyncSession, user_id: UUID, lecture_id: UUID, topic_index: int
) -> LessonUnlock | None:
    result = await session.execute(
        select(LessonUnlock).where(
            LessonUnlock.user_id == user_id,
            LessonUnlock.lecture_id == lecture_id,
            LessonUnlock.topic_index == topic_index,
        )
    )
    return result.scalar_one_or_none()


async def add_lesson_unlock(
    session: AsyncSession, *, user_id: UUID, lecture_id: UUID, topic_index: int
) -> LessonUnlock:
    unlock = LessonUnlock(user_id=user_id, lecture_id=lecture_id, topic_index=topic_index)
    session.add(unlock)
    await session.flush()
    return unlock


async def list_unlocked_lessons(
    session: AsyncSession, user_id: UUID, course_id: UUID
) -> set[tuple[UUID, int]]:
    """The (lecture_id, topic_index) pairs the learner has coin-unlocked in a course."""
    result = await session.execute(
        select(LessonUnlock.lecture_id, LessonUnlock.topic_index)
        .join(Lecture, Lecture.id == LessonUnlock.lecture_id)
        .where(Lecture.course_id == course_id, LessonUnlock.user_id == user_id)
    )
    return {(row[0], row[1]) for row in result.all()}


# --- Views ----------------------------------------------------------------


def to_player_view(profile: PlayerProfile, *, played_today: bool) -> PlayerView:
    return PlayerView(
        coins=profile.coins,
        lifetime_coins=profile.lifetime_coins,
        current_streak=profile.current_streak,
        longest_streak=profile.longest_streak,
        played_today=played_today,
        bonus_course_slots=profile.bonus_course_slots,
    )


def to_txn_view(txn: CoinTxn) -> CoinTxnView:
    return CoinTxnView(amount=txn.amount, reason=txn.reason, created_at=txn.created_at)
