"""Integration: per-topic lesson generation against real SQLite + a fake LLM."""

from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.course.dtos import DocDraft
from app.domains.course.repository import add_lecture, create_course, list_docs
from app.processes.course_generation.writer import generate_topic_doc
from tests.fixtures.fakes import FakeLlm

PROFILE = {"experience_level": "beginner", "weekly_time": "5 hours"}


async def test_generates_doc_for_a_single_topic(db_session: AsyncSession) -> None:
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
    await db_session.flush()

    model = FakeLlm(responses=[DocDraft(title="Loops", content="# Loops").model_dump_json()])

    doc = await generate_topic_doc(
        db_session, model=model, lecture=lecture, topic_index=2, profile=PROFILE
    )

    assert doc.position == 3  # topic_index 2 → position 3
    assert doc.content == "# Loops"

    persisted = await list_docs(db_session, lecture.id)
    assert [d.position for d in persisted] == [3]  # only the one topic was generated
