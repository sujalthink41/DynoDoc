"""E2E: complete an intake, then generate a course roadmap via the ADK pipeline.

Intake uses the FakeTextGenerator (the port); generation uses the FakeLlm (ADK's
model layer). Both keep the flow offline + deterministic.
"""

from httpx import AsyncClient

from app.domains.course.dtos import IntakeStep, LearnerProfile, Roadmap, RoadmapLecture
from tests.fixtures.fakes import FakeLlm, FakeTextGenerator


async def _login_and_complete_intake(
    client: AsyncClient, fake_text_generator: FakeTextGenerator
) -> str:
    await client.post("/api/v1/auth/dev-login", json={"email": "learner@example.com"})
    fake_text_generator.queue(
        IntakeStep(
            is_complete=True,
            profile=LearnerProfile(
                experience_level="beginner",
                background="none",
                goal="build scripts",
                weekly_time="3 hours",
            ),
        )
    )
    start = await client.post("/api/v1/intake", json={"goal": "Learn Python"})
    assert start.json()["status"] == "ready"
    return str(start.json()["id"])


async def test_generate_course_from_intake(
    client: AsyncClient,
    fake_text_generator: FakeTextGenerator,
    fake_llm: FakeLlm,
) -> None:
    intake_id = await _login_and_complete_intake(client, fake_text_generator)

    roadmap = Roadmap(
        title="Python Foundations",
        lectures=[
            RoadmapLecture(title="Setup & Basics", summary="Get going", topics=["install", "repl"]),
            RoadmapLecture(title="Data Types", summary="Core types", topics=["str", "int"]),
        ],
    )
    fake_llm.responses.append(roadmap.model_dump_json())

    response = await client.post("/api/v1/courses", json={"intake_id": intake_id})
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Python Foundations"
    assert [lec["position"] for lec in body["lectures"]] == [1, 2]
    assert body["lectures"][0]["title"] == "Setup & Basics"

    listing = await client.get("/api/v1/courses")
    assert listing.status_code == 200
    assert any(c["title"] == "Python Foundations" for c in listing.json())


async def test_cannot_generate_course_from_incomplete_intake(
    client: AsyncClient, fake_text_generator: FakeTextGenerator
) -> None:
    await client.post("/api/v1/auth/dev-login", json={"email": "learner@example.com"})
    fake_text_generator.queue(IntakeStep(is_complete=False, questions=["What's your level?"]))
    start = await client.post("/api/v1/intake", json={"goal": "Learn Python"})
    intake_id = start.json()["id"]

    response = await client.post("/api/v1/courses", json={"intake_id": intake_id})
    assert response.status_code == 409
    assert response.json()["code"] == "intake_not_ready"
