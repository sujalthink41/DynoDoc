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

    # First turn: the AI asks one focused question.
    fake_text_generator.queue(
        IntakeStep(on_topic=True, is_complete=False, message="What's your experience so far?")
    )
    start = await client.post("/api/v1/intake", json={"goal": "Learn Python"})
    assert start.status_code == 201
    body = start.json()
    assert body["status"] == "in_progress"
    # Transcript holds the goal then the assistant's single question.
    assert [t["role"] for t in body["transcript"]] == ["user", "assistant"]
    assert body["transcript"][-1]["content"] == "What's your experience so far?"
    intake_id = body["id"]

    # Second turn: the AI is satisfied and returns a profile.
    fake_text_generator.queue(
        IntakeStep(
            on_topic=True,
            is_complete=True,
            message="Perfect — building your plan!",
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


async def test_off_topic_request_is_refused(
    client: AsyncClient, fake_text_generator: FakeTextGenerator
) -> None:
    await _login(client)
    fake_text_generator.queue(
        IntakeStep(
            on_topic=False,
            is_complete=False,
            message="DynoDoc only builds technical learning courses — try a tech topic!",
        )
    )
    start = await client.post("/api/v1/intake", json={"goal": "Teach me to play guitar"})
    body = start.json()
    assert body["status"] == "in_progress"
    assert body["profile"] is None
    assert body["transcript"][-1]["role"] == "assistant"


async def test_intake_history_lists_past_sessions(
    client: AsyncClient, fake_text_generator: FakeTextGenerator
) -> None:
    await _login(client)
    fake_text_generator.queue(IntakeStep(on_topic=True, is_complete=False, message="What level?"))
    await client.post("/api/v1/intake", json={"goal": "Learn Rust"})

    history = await client.get("/api/v1/intake")
    assert history.status_code == 200
    items = history.json()
    assert len(items) == 1
    assert items[0]["goal"] == "Learn Rust"
    assert items[0]["status"] == "in_progress"
    assert "created_at" in items[0]
