"""E2E: the profile stats + achievements endpoint."""

from datetime import date

from httpx import AsyncClient

from app.domains.gamification import connections as conn
from tests.fixtures.fakes import FakeLlm, FakeTextGenerator


async def test_stats_start_empty(client: AsyncClient) -> None:
    await client.post("/api/v1/auth/dev-login", json={"email": "learner@example.com"})
    stats = (await client.get("/api/v1/me/stats")).json()
    assert stats["courses_count"] == 0
    assert stats["lessons_mastered"] == 0
    assert stats["unlocked_count"] == 0
    assert stats["total_achievements"] >= 8
    # Every achievement starts locked.
    assert all(not a["unlocked"] for a in stats["achievements"])


async def test_solving_connections_unlocks_progress(
    client: AsyncClient, fake_text_generator: FakeTextGenerator, fake_llm: FakeLlm
) -> None:
    await client.post("/api/v1/auth/dev-login", json={"email": "learner@example.com"})
    puzzle = conn.puzzle_for_date(date.today())
    groups = [list(group.members) for group in puzzle.groups]
    await client.post(
        "/api/v1/game/connections/attempt", json={"groups": groups, "duration_seconds": 20}
    )

    stats = (await client.get("/api/v1/me/stats")).json()
    assert stats["connections_solved"] == 1
    assert stats["lifetime_coins"] == 10
    # The "first course" badge is still locked; coin/streak progress is tracked.
    by_key = {a["key"]: a for a in stats["achievements"]}
    assert by_key["puzzler"]["current"] == 1
    assert by_key["puzzler"]["unlocked"] is False
