"""E2E: generate a lecture's lesson docs (writer fan-out) — all with a fake LLM."""

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


async def test_generate_lecture_docs(
    client: AsyncClient, fake_text_generator: FakeTextGenerator, fake_llm: FakeLlm
) -> None:
    lecture_id = await _make_course_with_lecture(client, fake_text_generator, fake_llm)

    # One canned doc per topic (the lecture has 2 topics).
    fake_llm.responses.append(DocDraft(title="Variables", content="# Variables").model_dump_json())
    fake_llm.responses.append(DocDraft(title="Loops", content="# Loops").model_dump_json())

    response = await client.post(f"/api/v1/lectures/{lecture_id}/generate")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready"
    assert [doc["position"] for doc in body["docs"]] == [1, 2]
    assert all(doc["content"] for doc in body["docs"])

    # Idempotent: regenerating returns the same docs without calling the LLM again.
    again = await client.post(f"/api/v1/lectures/{lecture_id}/generate")
    assert again.status_code == 200
    assert len(again.json()["docs"]) == 2


async def test_get_lecture_returns_docs(
    client: AsyncClient, fake_text_generator: FakeTextGenerator, fake_llm: FakeLlm
) -> None:
    lecture_id = await _make_course_with_lecture(client, fake_text_generator, fake_llm)
    fake_llm.responses.append(DocDraft(title="Variables", content="# Variables").model_dump_json())
    fake_llm.responses.append(DocDraft(title="Loops", content="# Loops").model_dump_json())
    await client.post(f"/api/v1/lectures/{lecture_id}/generate")

    response = await client.get(f"/api/v1/lectures/{lecture_id}")
    assert response.status_code == 200
    assert len(response.json()["docs"]) == 2


async def test_generated_lecture_includes_curated_references(
    client: AsyncClient,
    fake_text_generator: FakeTextGenerator,
    fake_llm: FakeLlm,
    fake_curator: FakeResourceCurator,
) -> None:
    lecture_id = await _make_course_with_lecture(client, fake_text_generator, fake_llm)
    fake_llm.responses.append(DocDraft(title="Variables", content="# Variables").model_dump_json())
    fake_llm.responses.append(DocDraft(title="Loops", content="# Loops").model_dump_json())
    fake_curator.references = [
        ReferenceDraft(type="article", url="https://realpython.com/x", title="Real Python"),
        ReferenceDraft(type="youtube", url="https://youtube.com/watch?v=1", title="Video"),
    ]

    response = await client.post(f"/api/v1/lectures/{lecture_id}/generate")
    assert response.status_code == 200
    refs = response.json()["references"]
    assert [r["type"] for r in refs] == ["article", "youtube"]
    assert refs[0]["url"] == "https://realpython.com/x"
