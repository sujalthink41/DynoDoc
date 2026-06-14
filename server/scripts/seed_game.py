"""Dev helper: seed a learner's gamification state so you can eyeball the UI.

Gives the user some DynoCoins + an active streak, with `last_activity_date` set
to YESTERDAY — so "played today" is False and the navbar/dashboard "play today"
nudges show. Pass --played to also mark today's Connections as done.

Usage (from the `server/` directory):
    uv run python -m scripts.seed_game                 # most recently created user
    uv run python -m scripts.seed_game --email a@b.com
    uv run python -m scripts.seed_game --played        # simulate already played today
"""

import argparse
import asyncio
from datetime import date, timedelta

from sqlalchemy import select

from app.domains.gamification import connections as conn
from app.domains.gamification.models import GamePlay, PlayerProfile
from app.domains.user.models import User
from app.platform.persistence.database import build_database
from app.runtime.settings import get_settings


async def seed(email: str | None, played: bool) -> None:
    db = build_database(get_settings())
    async with db.sessionmaker() as session:
        if email:
            result = await session.execute(select(User).where(User.email == email))
        else:
            result = await session.execute(select(User).order_by(User.created_at.desc()).limit(1))
        user = result.scalars().first()
        if user is None:
            print("No user found — log in once first, then re-run.")
            return

        profile = (
            await session.execute(select(PlayerProfile).where(PlayerProfile.user_id == user.id))
        ).scalar_one_or_none()
        if profile is None:
            profile = PlayerProfile(user_id=user.id)
            session.add(profile)

        today = date.today()
        profile.coins = 1500  # enough to test redeeming a reward (1000) + a course slot (500)
        profile.lifetime_coins = 1600
        profile.current_streak = 6
        profile.longest_streak = 9
        profile.last_activity_date = today if played else today - timedelta(days=1)

        if played:
            existing = (
                await session.execute(
                    select(GamePlay).where(
                        GamePlay.user_id == user.id,
                        GamePlay.game_key == conn.GAME_KEY,
                        GamePlay.play_date == today,
                    )
                )
            ).scalar_one_or_none()
            if existing is None:
                session.add(
                    GamePlay(
                        user_id=user.id,
                        game_key=conn.GAME_KEY,
                        play_date=today,
                        solved=True,
                        score=4,
                        duration_seconds=42,
                        coins_awarded=65,
                    )
                )

        await session.commit()
        print(
            f"Seeded {user.email}: coins={profile.coins}, streak={profile.current_streak}, "
            f"played_today={'yes' if played else 'no'}."
        )
    await db.engine.dispose()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--email", default=None, help="target user email (default: newest user)")
    parser.add_argument("--played", action="store_true", help="also mark today's game as played")
    args = parser.parse_args()
    asyncio.run(seed(args.email, args.played))


if __name__ == "__main__":
    main()
