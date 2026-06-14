"""Aggregate a learner's cross-domain stats and evaluate their achievements."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.course.progress import compute_lessons
from app.domains.course.repository import list_courses
from app.domains.gamification import connections as conn
from app.domains.gamification.achievements import evaluate
from app.domains.gamification.dtos import ProfileStatsView
from app.domains.gamification.repository import (
    game_play_counts,
    get_or_create_profile,
    player_rank,
)

_MASTERY_SCORE = 100


async def build_profile_stats(session: AsyncSession, *, user_id: UUID) -> ProfileStatsView:
    courses = await list_courses(session, user_id)
    lessons_passed = 0
    lessons_mastered = 0
    courses_completed = 0
    for course in courses:
        lessons = await compute_lessons(session, course.id, user_id)
        if not lessons:
            continue
        passed = sum(1 for lesson in lessons if lesson.passed)
        lessons_passed += passed
        lessons_mastered += sum(1 for lesson in lessons if lesson.score >= _MASTERY_SCORE)
        if passed == len(lessons):
            courses_completed += 1

    played, solved = await game_play_counts(session, user_id, conn.GAME_KEY)
    profile = await get_or_create_profile(session, user_id)
    rank = await player_rank(session, profile.lifetime_coins)

    stats = {
        "courses_count": len(courses),
        "courses_completed": courses_completed,
        "lessons_passed": lessons_passed,
        "lessons_mastered": lessons_mastered,
        "connections_solved": solved,
        "longest_streak": profile.longest_streak,
        "lifetime_coins": profile.lifetime_coins,
    }
    achievements = evaluate(stats)

    return ProfileStatsView(
        coins=profile.coins,
        lifetime_coins=profile.lifetime_coins,
        current_streak=profile.current_streak,
        longest_streak=profile.longest_streak,
        rank=rank,
        courses_count=len(courses),
        courses_completed=courses_completed,
        lessons_passed=lessons_passed,
        lessons_mastered=lessons_mastered,
        connections_played=played,
        connections_solved=solved,
        unlocked_count=sum(1 for a in achievements if a.unlocked),
        total_achievements=len(achievements),
        achievements=achievements,
    )
