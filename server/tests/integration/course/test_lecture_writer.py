"""Integration: per-topic writer fan-out against real SQLite + a fake LLM."""

from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.course.dtos import DocDraft
from app.domains.course.repository import add_lecture, create_course, list_docs
from app.processes.course_generation.writer import generate_lecture_docs
from tests.fixtures.fakes import FakeLlm

PROFILE = {"experience_level": "beginner", "weekly_time": "5 hours"}


async def test_generates_one_doc_per_topic(db_session: AsyncSession) -> None:
    course = await create_course(
        db_session,
        owner_user_id=uuid4(),
        intake_session_id=uuid4(),
        title="Python",
        goal="Learn Python",
        learner_profile=PROFILE,
    )
    lecture = await add_lecture(
        db_session,
        course_id=course.id,
        position=1,
        title="Basics",
        summary="Core ideas",
        topics=["variables", "types", "loops"],
    )
    await db_session.flush()  # assign lecture.id

    # One canned doc per topic (3). Order among concurrent writers doesn't matter;
    # docs are persisted in topic order with positions 1..N.
    model = FakeLlm(
        responses=[
            DocDraft(title=f"Doc {i}", content=f"# Lesson {i}").model_dump_json() for i in range(3)
        ]
    )

    docs = await generate_lecture_docs(db_session, model=model, lecture=lecture, profile=PROFILE)

    assert len(docs) == 3
    assert lecture.status == "ready"

    persisted = await list_docs(db_session, lecture.id)
    assert [doc.position for doc in persisted] == [1, 2, 3]
    assert all(doc.content.startswith("# Lesson") for doc in persisted)
