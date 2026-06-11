"""E2E: per-topic lesson generation + separate references — all with a fake LLM."""

from httpx import AsyncClient

from app.domains.course.dtos import (
    DocDraft,
    IntakeStep,
    LearnerProfile,
    Roadmap,
    RoadmapLecture,
)
from app.shared.contracts.curation import ReferenceDraft
from tests.fixtures.fakes import FakeLlm, FakeResourceCurator, FakeTextGenerator


async def _make_course_with_lecture(
    client: AsyncClient, fake_text_generator: FakeTextGenerator, fake_llm: FakeLlm
) -> str:
    await client.post("/api/v1/auth/dev-login", json={"email": "learner@example.com"})
    fake_text_generator.queue(
        IntakeStep(
            is_complete=True,
            profile=LearnerProfile(
                experience_level="beginner", background="none", goal="scripts", weekly_time="3h"
            ),
        )
    )
    intake = await client.post("/api/v1/intake", json={"goal": "Learn Python"})
    intake_id = intake.json()["id"]

    fake_llm.responses.append(
        Roadmap(
            title="Python",
            lectures=[
                RoadmapLecture(title="Basics", summary="Core ideas", topics=["variables", "loops"])
            ],
        ).model_dump_json()
    )
    course = await client.post("/api/v1/courses", json={"intake_id": intake_id})
    return str(course.json()["lectures"][0]["id"])


async def test_generate_single_topic(
    client: AsyncClient, fake_text_generator: FakeTextGenerator, fake_llm: FakeLlm
) -> None:
    lecture_id = await _make_course_with_lecture(client, fake_text_generator, fake_llm)

    fake_llm.responses.append(DocDraft(title="Variables", content="# Variables").model_dump_json())
    response = await client.post(f"/api/v1/lectures/{lecture_id}/topics/0")
    assert response.status_code == 200
    body = response.json()
    # Only topic 0 generated → one doc at position 1, lecture still in progress.
    assert [d["position"] for d in body["docs"]] == [1]
    assert body["status"] == "in_progress"

    # Generating the second topic completes the lecture.
    fake_llm.responses.append(DocDraft(title="Loops", content="# Loops").model_dump_json())
    response = await client.post(f"/api/v1/lectures/{lecture_id}/topics/1")
    body = response.json()
    assert [d["position"] for d in body["docs"]] == [1, 2]
    assert body["status"] == "ready"


async def test_find_resources_button(
    client: AsyncClient,
    fake_text_generator: FakeTextGenerator,
    fake_llm: FakeLlm,
    fake_curator: FakeResourceCurator,
) -> None:
    lecture_id = await _make_course_with_lecture(client, fake_text_generator, fake_llm)
    fake_curator.references = [
        ReferenceDraft(type="article", url="https://realpython.com/x", title="Real Python"),
        ReferenceDraft(type="youtube", url="https://youtube.com/watch?v=1", title="Video"),
    ]

    response = await client.post(f"/api/v1/lectures/{lecture_id}/references")
    assert response.status_code == 200
    refs = response.json()["references"]
    assert [r["type"] for r in refs] == ["article", "youtube"]
