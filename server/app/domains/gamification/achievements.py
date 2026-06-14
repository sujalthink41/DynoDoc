"""Achievement catalog + evaluation — milestones a learner unlocks over time.

Pure logic: given a dict of the learner's stats, decide which badges are earned
and how close the rest are. The catalog is the single source of truth.
"""

from dataclasses import dataclass

from app.domains.gamification.dtos import AchievementView


@dataclass(frozen=True)
class AchievementDef:
    key: str
    title: str
    description: str
    icon: str
    stat: str  # which stat in the stats dict to measure
    goal: int


CATALOG: list[AchievementDef] = [
    AchievementDef(
        "first_course", "First Steps", "Create your first course", "🚀", "courses_count", 1
    ),
    AchievementDef("scholar", "Scholar", "Pass 10 lessons", "📚", "lessons_passed", 10),
    AchievementDef(
        "perfectionist", "Perfectionist", "Master 5 lessons at 100%", "💯", "lessons_mastered", 5
    ),
    AchievementDef("graduate", "Graduate", "Complete a whole course", "🎓", "courses_completed", 1),
    AchievementDef("on_fire", "On Fire", "Reach a 7-day streak", "🔥", "longest_streak", 7),
    AchievementDef(
        "unstoppable", "Unstoppable", "Reach a 30-day streak", "⚡", "longest_streak", 30
    ),
    AchievementDef(
        "coin_collector",
        "Coin Collector",
        "Earn 500 lifetime DynoCoins",
        "🪙",
        "lifetime_coins",
        500,
    ),
    AchievementDef(
        "high_roller", "High Roller", "Earn 2000 lifetime DynoCoins", "💰", "lifetime_coins", 2000
    ),
    AchievementDef(
        "puzzler", "Puzzler", "Solve 5 Connections puzzles", "🧩", "connections_solved", 5
    ),
]


def evaluate(stats: dict[str, int]) -> list[AchievementView]:
    views: list[AchievementView] = []
    for item in CATALOG:
        current = stats.get(item.stat, 0)
        views.append(
            AchievementView(
                key=item.key,
                title=item.title,
                description=item.description,
                icon=item.icon,
                goal=item.goal,
                current=min(current, item.goal),
                unlocked=current >= item.goal,
            )
        )
    return views
