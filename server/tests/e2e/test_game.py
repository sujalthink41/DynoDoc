"""E2E: DynoCoin wallet, Connections game, leaderboard, quiz coins, lesson unlock."""

from datetime import date

from httpx import AsyncClient

from app.domains.course.dtos import (
    DocDraft,
    IntakeStep,
    LearnerProfile,
    QuizQuestion,
    QuizSpec,
    Roadmap,
    RoadmapLecture,
)
from app.domains.gamification import connections as conn
from tests.fixtures.fakes import FakeLlm, FakeTextGenerator


async def _login(client: AsyncClient, email: str = "learner@example.com") -> None:
    await client.post("/api/v1/auth/dev-login", json={"email": email})


async def _course_with_first_lesson(
    client: AsyncClient, fake_text_generator: FakeTextGenerator, fake_llm: FakeLlm
) -> str:
    await _login(client)
    fake_text_generator.queue(
        IntakeStep(
            is_complete=True,
            profile=LearnerProfile(
                experience_level="beginner", background="none", goal="scripts", weekly_time="3h"
            ),
        )
    )
    intake = await client.post("/api/v1/intake", json={"goal": "Learn Python"})
    fake_llm.responses.append(
        Roadmap(
            title="Python",
            lectures=[
                RoadmapLecture(title="Basics", summary="Core ideas", topics=["variables", "loops"])
            ],
        ).model_dump_json()
    )
    course = await client.post("/api/v1/courses", json={"intake_id": intake.json()["id"]})
    lecture_id = str(course.json()["lectures"][0]["id"])
    fake_llm.responses.append(DocDraft(title="Variables", content="# Variables").model_dump_json())
    await client.post(f"/api/v1/lectures/{lecture_id}/topics/0")
    return lecture_id


async def test_profile_starts_at_zero(client: AsyncClient) -> None:
    await _login(client)
    body = (await client.get("/api/v1/game/profile")).json()
    assert body["coins"] == 0
    assert body["lifetime_coins"] == 0
    assert body["played_today"] is False


async def test_connections_board_hides_answers(client: AsyncClient) -> None:
    await _login(client)
    response = await client.get("/api/v1/game/connections")
    assert response.status_code == 200
    body = response.json()
    assert len(body["tiles"]) == 16
    assert body["group_count"] == 4
    assert body["played"] is False


async def test_connections_solve_awards_coins_and_streak(client: AsyncClient) -> None:
    await _login(client)
    await client.get("/api/v1/game/connections")  # ensure today's board is available

    puzzle = conn.puzzle_for_date(date.today())
    groups = [list(group.members) for group in puzzle.groups]
    attempt = await client.post(
        "/api/v1/game/connections/attempt", json={"groups": groups, "duration_seconds": 20}
    )
    assert attempt.status_code == 200
    result = attempt.json()
    assert result["solved"] is True
    assert result["correct_groups"] == 4
    # 8/group * 4 + 18 solve bonus + 15 speed (<=30s) = 65, day-1 streak (no milestone).
    assert result["coins_awarded"] == 65
    assert result["current_streak"] == 1
    assert result["new_balance"] == 65
    assert len(result["groups"]) == 4  # answer key revealed after submit

    # Replaying the same day is blocked.
    replay = await client.post("/api/v1/game/connections/attempt", json={"groups": groups})
    assert replay.status_code == 409
    assert replay.json()["code"] == "already_played"

    profile = (await client.get("/api/v1/game/profile")).json()
    assert profile["played_today"] is True
    assert profile["lifetime_coins"] == 65


async def test_leaderboards_all_time_and_today(client: AsyncClient) -> None:
    await _login(client)
    puzzle = conn.puzzle_for_date(date.today())
    groups = [list(group.members) for group in puzzle.groups]
    await client.post(
        "/api/v1/game/connections/attempt", json={"groups": groups, "duration_seconds": 20}
    )

    all_time = (await client.get("/api/v1/game/leaderboard?period=all")).json()
    assert all_time["period"] == "all"
    assert all_time["me"]["is_me"] is True
    assert all_time["me"]["coins"] == 65
    assert any(entry["is_me"] for entry in all_time["top"])

    today = (await client.get("/api/v1/game/leaderboard?period=today")).json()
    assert today["period"] == "today"
    assert today["me"]["correct"] == 4
    assert today["me"]["duration_seconds"] == 20
    assert today["top"][0]["is_me"] is True


async def test_quiz_pass_and_mastery_award_coins(
    client: AsyncClient, fake_text_generator: FakeTextGenerator, fake_llm: FakeLlm
) -> None:
    lecture_id = await _course_with_first_lesson(client, fake_text_generator, fake_llm)
    fake_llm.responses.append(
        QuizSpec(
            questions=[QuizQuestion(question="Q?", options=["a", "b"], answer_index=1)] * 5
        ).model_dump_json()
    )
    await client.post(f"/api/v1/lectures/{lecture_id}/topics/0/quiz")
    await client.post(
        f"/api/v1/lectures/{lecture_id}/topics/0/quiz/attempt", json={"answers": [1, 1, 1, 1, 1]}
    )
    profile = (await client.get("/api/v1/game/profile")).json()
    assert profile["coins"] == 40  # pass (15) + mastery (25)


async def test_unlock_requires_enough_coins(
    client: AsyncClient, fake_text_generator: FakeTextGenerator, fake_llm: FakeLlm
) -> None:
    lecture_id = await _course_with_first_lesson(client, fake_text_generator, fake_llm)
    response = await client.post(f"/api/v1/lectures/{lecture_id}/topics/1/unlock")
    assert response.status_code == 402
    assert response.json()["code"] == "insufficient_coins"
