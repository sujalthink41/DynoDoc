"""E2E: the intake flow over HTTP, with a fake LLM injected."""

from httpx import AsyncClient

from app.domains.course.dtos import IntakeStep, LearnerProfile
from tests.fixtures.fakes import FakeTextGenerator


async def _login(client: AsyncClient) -> None:
    await client.post("/api/v1/auth/dev-login", json={"email": "learner@example.com"})


async def test_intake_requires_authentication(client: AsyncClient) -> None:
    response = await client.post("/api/v1/intake", json={"goal": "Learn Python"})
    assert response.status_code == 401


async def test_full_intake_flow(
    client: AsyncClient, fake_text_generator: FakeTextGenerator
) -> None:
    await _login(client)

    # First turn: the AI asks questions.
    fake_text_generator.queue(
        IntakeStep(is_complete=False, questions=["What's your experience?", "Hours per week?"])
    )
    start = await client.post("/api/v1/intake", json={"goal": "Learn Python"})
    assert start.status_code == 201
    body = start.json()
    assert body["status"] == "in_progress"
    assert body["questions"] == ["What's your experience?", "Hours per week?"]
    intake_id = body["id"]

    # Second turn: the AI is satisfied and returns a profile.
    fake_text_generator.queue(
        IntakeStep(
            is_complete=True,
            profile=LearnerProfile(
                experience_level="beginner",
                background="none",
                goal="build small scripts",
                weekly_time="3 hours",
            ),
        )
    )
    answered = await client.post(
        f"/api/v1/intake/{intake_id}/answer", json={"answer": "total beginner, ~3h/week"}
    )
    assert answered.status_code == 200
    result = answered.json()
    assert result["status"] == "ready"
    assert result["profile"]["experience_level"] == "beginner"
    assert result["questions"] == []
