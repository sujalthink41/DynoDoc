"""Integration: the in-lesson tutor against real SQLite + a fake LLM."""

from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.course.dtos import TutorReply, TutorTurn
from app.domains.course.repository import add_doc, add_lecture, create_course
from app.processes.tutoring.answer import answer_lesson_question
from app.shared.errors import ValidationError
from tests.fixtures.fakes import FakeLlm


async def _lesson(db_session: AsyncSession):  # type: ignore[no-untyped-def]
    course = await create_course(
        db_session,
        owner_user_id=uuid4(),
        intake_session_id=uuid4(),
        title="Python",
        goal="Learn Python",
        learner_profile={"experience_level": "beginner"},
    )
    lecture = await add_lecture(
        db_session,
        course_id=course.id,
        position=1,
        title="Basics",
        summary="Core ideas",
        topics=["variables", "loops"],
    )
    await db_session.flush()
    return lecture


async def test_tutor_answers_grounded_question(db_session: AsyncSession) -> None:
    lecture = await _lesson(db_session)
    await add_doc(
        db_session, lecture_id=lecture.id, position=1, title="Variables", content="# Variables"
    )
    await db_session.flush()

    model = FakeLlm(
        responses=[TutorReply(on_topic=True, answer="A variable stores a value.").model_dump_json()]
    )
    reply = await answer_lesson_question(
        db_session,
        model=model,
        lecture=lecture,
        topic_index=0,
        question="What is a variable?",
        history=[TutorTurn(role="user", content="hi")],
    )

    assert reply.on_topic is True
    assert "variable" in reply.answer.lower()


async def test_tutor_requires_generated_lesson(db_session: AsyncSession) -> None:
    lecture = await _lesson(db_session)  # no doc generated for topic 0
    model = FakeLlm(responses=[TutorReply(answer="…").model_dump_json()])

    with pytest.raises(ValidationError) as err:
        await answer_lesson_question(
            db_session,
            model=model,
            lecture=lecture,
            topic_index=0,
            question="explain",
            history=[],
        )
    assert err.value.code == "lesson_not_generated"
