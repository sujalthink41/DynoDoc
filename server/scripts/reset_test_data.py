"""Dev helper: wipe a learner's courses + game plays so flows can be re-tested.

Clears the things that block re-testing:
- all courses (cascades to lectures/docs/quizzes/references/progress/unlocks) →
  frees up the 3-roadmap free limit
- all game plays → "played today" resets so the not-played nudges show and you
  can play Connections again
- intake sessions → a clean chat history

Coins/streak on the PlayerProfile are left intact. Usage (from `server/`):
    uv run python -m scripts.reset_test_data                # newest user
    uv run python -m scripts.reset_test_data --email a@b.com
"""

import argparse
import asyncio

from sqlalchemy import delete, select

from app.domains.course.models import Course, IntakeSession
from app.domains.gamification.models import GamePlay
from app.domains.user.models import User
from app.platform.persistence.database import build_database
from app.runtime.settings import get_settings


async def reset(email: str | None) -> None:
    db = build_database(get_settings())
    async with db.sessionmaker() as session:
        if email:
            result = await session.execute(select(User).where(User.email == email))
        else:
            result = await session.execute(select(User).order_by(User.created_at.desc()).limit(1))
        user = result.scalars().first()
        if user is None:
            print("No user found.")
            return

        courses = await session.execute(delete(Course).where(Course.owner_user_id == user.id))
        intakes = await session.execute(
            delete(IntakeSession).where(IntakeSession.owner_user_id == user.id)
        )
        games = await session.execute(delete(GamePlay).where(GamePlay.user_id == user.id))
        await session.commit()
        n_courses = courses.rowcount  # type: ignore[attr-defined]
        n_intakes = intakes.rowcount  # type: ignore[attr-defined]
        n_games = games.rowcount  # type: ignore[attr-defined]
        print(
            f"Reset {user.email}: removed {n_courses} course(s), "
            f"{n_intakes} intake(s), {n_games} game play(s). "
            "Coins/streak kept; you can build roadmaps and play again."
        )
    await db.engine.dispose()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--email", default=None, help="target user email (default: newest user)")
    args = parser.parse_args()
    asyncio.run(reset(args.email))


if __name__ == "__main__":
    main()
