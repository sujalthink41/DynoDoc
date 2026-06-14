"""Settle a day's Connections leaderboard, awarding the nightly top-3 bonus.

This is the same logic the `/game/settle-daily` cron endpoint runs; handy for a
manual run or backfill. Idempotent per day.

Usage (from the `server/` directory):
    uv run python -m scripts.settle_daily               # settle yesterday
    uv run python -m scripts.settle_daily --date 2026-06-13
"""

import argparse
import asyncio
from datetime import date, timedelta

from app.domains.gamification import connections as conn
from app.domains.gamification.repository import settle_daily_leaderboard
from app.platform.persistence.database import build_database
from app.runtime.settings import get_settings


async def settle(target: str | None) -> None:
    day = date.fromisoformat(target) if target else date.today() - timedelta(days=1)
    db = build_database(get_settings())
    async with db.sessionmaker() as session:
        awarded = await settle_daily_leaderboard(session, game_key=conn.GAME_KEY, day=day)
        await session.commit()
    await db.engine.dispose()

    if not awarded:
        print(f"{day}: nothing to settle (already done, or nobody solved it).")
        return
    for user_id, rank, coins in awarded:
        print(f"{day}: rank #{rank} -> {coins} coins (user {user_id})")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--date", default=None, help="day to settle (YYYY-MM-DD); default: yesterday"
    )
    args = parser.parse_args()
    asyncio.run(settle(args.date))


if __name__ == "__main__":
    main()
