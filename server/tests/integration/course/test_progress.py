"""Integration: sequential unlocking, quiz generation, and progress aggregation."""

from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.course.dtos import QuizQuestion, QuizSpec
from app.domains.course.progress import build_course_view, compute_lessons
from app.domains.course.repository import (
    add_doc,
    add_lecture,
    create_course,
    record_quiz_score,
)
from app.processes.course_generation.quiz import generate_quiz
from tests.fixtures.fakes import FakeLlm


async def _course_with_two_lessons(session: AsyncSession, user_id):  # type: ignore[no-untyped-def]
    course = await create_course(
        session,
        owner_user_id=user_id,
        intake_session_id=uuid4(),
        title="Python",
        goal="Learn Python",
        learner_profile={"experience_level": "beginner"},
    )
    lecture = await add_lecture(
        session,
        course_id=course.id,
        position=1,
        title="Basics",
        summary="Core ideas",
        topics=["variables", "loops"],
    )
    await session.flush()
    return course, lecture


async def test_only_first_lesson_unlocked_initially(db_session: AsyncSession) -> None:
    user_id = uuid4()
    course, _ = await _course_with_two_lessons(db_session, user_id)

    lessons = await compute_lessons(db_session, course.id, user_id)
    assert [lesson.unlocked for lesson in lessons] == [True, False]
    assert all(not lesson.passed for lesson in lessons)


async def test_passing_unlocks_next_and_updates_aggregates(db_session: AsyncSession) -> None:
    user_id = uuid4()
    course, lecture = await _course_with_two_lessons(db_session, user_id)

    await record_quiz_score(
        db_session, user_id=user_id, lecture_id=lecture.id, topic_index=0, score=80
    )

    lessons = await compute_lessons(db_session, course.id, user_id)
    assert [lesson.unlocked for lesson in lessons] == [True, True]
    assert [lesson.passed for lesson in lessons] == [True, False]

    view = await build_course_view(db_session, user_id=user_id, course=course)
    assert view.completion_percent == 50  # 1 of 2 lessons passed
    assert view.average_score == 80  # one attempted lesson, best score 80
    assert view.lectures[0].lessons_passed == 1


async def test_best_score_is_kept_across_attempts(db_session: AsyncSession) -> None:
    user_id = uuid4()
    _, lecture = await _course_with_two_lessons(db_session, user_id)

    await record_quiz_score(
        db_session, user_id=user_id, lecture_id=lecture.id, topic_index=0, score=40
    )
    progress = await record_quiz_score(
        db_session, user_id=user_id, lecture_id=lecture.id, topic_index=0, score=90
    )
    assert progress.best_score == 90
    assert progress.passed is True
    assert progress.attempts == 2


async def test_generate_quiz_is_cached(db_session: AsyncSession) -> None:
    user_id = uuid4()
    _, lecture = await _course_with_two_lessons(db_session, user_id)
    await add_doc(db_session, lecture_id=lecture.id, position=1, title="Vars", content="# Vars")
    await db_session.flush()

    spec = QuizSpec(
        questions=[QuizQuestion(question="Q?", options=["a", "b", "c", "d"], answer_index=2)] * 5
    )
    model = FakeLlm(responses=[spec.model_dump_json()])

    first = await generate_quiz(db_session, model=model, lecture=lecture, topic_index=0)
    assert len(first.questions) == 5

    # No more queued responses — a second call must return the cached quiz, not call the LLM.
    second = await generate_quiz(db_session, model=model, lecture=lecture, topic_index=0)
    assert second.id == first.id
