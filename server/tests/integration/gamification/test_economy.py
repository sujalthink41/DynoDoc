"""Integration: DynoCoin economy, streak rules, Connections grading, unlocks."""

from datetime import date, timedelta
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.course.progress import compute_lessons
from app.domains.course.repository import add_lecture, create_course
from app.domains.gamification import connections as conn
from app.domains.gamification.models import PlayerProfile
from app.domains.gamification.repository import (
    add_lesson_unlock,
    award_coins,
    bump_streak,
    get_or_create_profile,
    leaderboard_top,
    list_unlocked_lessons,
    player_rank,
    spend_coins,
)
from app.shared.errors import AppError


async def test_award_tracks_balance_and_lifetime(db_session: AsyncSession) -> None:
    user_id = uuid4()
    await award_coins(db_session, user_id=user_id, amount=40, reason="connections")
    profile = await spend_coins(db_session, user_id=user_id, amount=30, reason="unlock_lesson")
    assert profile.coins == 10
    assert profile.lifetime_coins == 40  # spending never lowers lifetime earnings


async def test_spend_beyond_balance_raises(db_session: AsyncSession) -> None:
    user_id = uuid4()
    await award_coins(db_session, user_id=user_id, amount=10, reason="connections")
    with pytest.raises(AppError) as err:
        await spend_coins(db_session, user_id=user_id, amount=50, reason="unlock_lesson")
    assert err.value.code == "insufficient_coins"
    assert err.value.status_code == 402


def test_bump_streak_consecutive_gap_and_milestone() -> None:
    profile = PlayerProfile(
        user_id=uuid4(),
        coins=0,
        lifetime_coins=0,
        current_streak=0,
        longest_streak=0,
        last_activity_date=None,
    )
    day = date(2026, 6, 1)
    assert bump_streak(profile, day) == 0  # day 1
    assert bump_streak(profile, day + timedelta(days=1)) == 0  # day 2
    assert bump_streak(profile, day + timedelta(days=2)) == 20  # day 3 → milestone
    assert profile.current_streak == 3
    assert bump_streak(profile, day + timedelta(days=5)) == 0  # missed days → reset
    assert profile.current_streak == 1
    assert profile.longest_streak == 3
    assert bump_streak(profile, day + timedelta(days=5)) == 0  # same day → no double count
    assert profile.current_streak == 1


def test_connections_daily_puzzle_is_stable_and_gradable() -> None:
    day = date(2026, 6, 1)
    puzzle = conn.puzzle_for_date(day)
    assert len(puzzle.groups) == 4
    tiles = conn.daily_tiles(puzzle, day)
    assert len(tiles) == 16
    # Same day → same board for everyone.
    assert conn.daily_tiles(puzzle, day) == tiles

    # Grading the exact answer groups scores 4/4.
    correct_guess = [list(group.members) for group in puzzle.groups]
    assert conn.grade(puzzle, correct_guess) == 4
    # Swapping one member between the first two groups breaks BOTH of them.
    g0, g1, g2, g3 = puzzle.groups
    wrong = [
        [g0.members[0], g0.members[1], g0.members[2], g1.members[0]],
        [g1.members[1], g1.members[2], g1.members[3], g0.members[3]],
        list(g2.members),
        list(g3.members),
    ]
    assert conn.grade(puzzle, wrong) == 2  # only the two intact groups score


async def test_leaderboard_ranks_by_lifetime_coins(db_session: AsyncSession) -> None:
    low = uuid4()
    high = uuid4()
    await award_coins(db_session, user_id=low, amount=30, reason="connections")
    await award_coins(db_session, user_id=high, amount=90, reason="connections")
    # Rank is by lifetime coins, so the 90-coin player is ahead.
    assert await player_rank(db_session, 90) == 1
    assert await player_rank(db_session, 30) == 2


async def test_purchased_unlock_grants_read_only_access(db_session: AsyncSession) -> None:
    user_id = uuid4()
    course = await create_course(
        db_session,
        owner_user_id=user_id,
        intake_session_id=uuid4(),
        title="Python",
        goal="Learn Python",
        learner_profile={},
    )
    lecture = await add_lecture(
        db_session,
        course_id=course.id,
        position=1,
        title="Basics",
        summary="x",
        topics=["a", "b", "c"],
    )
    await db_session.flush()

    await add_lesson_unlock(db_session, user_id=user_id, lecture_id=lecture.id, topic_index=1)
    assert await list_unlocked_lessons(db_session, user_id, course.id) == {(lecture.id, 1)}

    lessons = await compute_lessons(db_session, course.id, user_id)
    # [0] first (open), [1] purchased (open), [2] still locked (purchase doesn't propagate).
    assert [lesson.unlocked for lesson in lessons] == [True, True, False]
    assert all(not lesson.passed for lesson in lessons)


async def test_profile_starts_empty(db_session: AsyncSession) -> None:
    profile = await get_or_create_profile(db_session, uuid4())
    assert profile.coins == 0
    assert profile.lifetime_coins == 0
    assert profile.current_streak == 0
    # leaderboard_top works on an empty table.
    assert await leaderboard_top(db_session) == []
