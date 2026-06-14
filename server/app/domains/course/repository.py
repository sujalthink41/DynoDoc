"""Course-domain persistence (plain async functions over an AsyncSession)."""

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.course.dtos import (
    DocView,
    IntakeSessionView,
    IntakeSummary,
    LearnerProfile,
    ReferenceView,
    TranscriptTurn,
)
from app.domains.course.models import (
    Course,
    Doc,
    IntakeSession,
    Lecture,
    LessonProgress,
    Quiz,
    Reference,
)


async def create_intake_session(
    session: AsyncSession, *, owner_user_id: UUID, goal: str
) -> IntakeSession:
    intake = IntakeSession(
        owner_user_id=owner_user_id, goal=goal, transcript=[], pending_questions=[]
    )
    session.add(intake)
    await session.flush()
    return intake


async def get_intake_session(session: AsyncSession, intake_id: UUID) -> IntakeSession | None:
    return await session.get(IntakeSession, intake_id)


async def list_intake_sessions(session: AsyncSession, owner_user_id: UUID) -> list[IntakeSession]:
    result = await session.execute(
        select(IntakeSession)
        .where(IntakeSession.owner_user_id == owner_user_id)
        .order_by(IntakeSession.created_at.desc())
    )
    return list(result.scalars().all())


def to_view(intake: IntakeSession) -> IntakeSessionView:
    return IntakeSessionView(
        id=intake.id,
        status=intake.status,
        goal=intake.goal,
        transcript=[
            TranscriptTurn(role=turn["role"], content=turn["content"]) for turn in intake.transcript
        ],
        profile=LearnerProfile(**intake.profile) if intake.profile else None,
    )


def to_intake_summary(intake: IntakeSession) -> IntakeSummary:
    return IntakeSummary(
        id=intake.id, goal=intake.goal, status=intake.status, created_at=intake.created_at
    )


# --- Course / Lecture -----------------------------------------------------


async def create_course(
    session: AsyncSession,
    *,
    owner_user_id: UUID,
    intake_session_id: UUID | None,
    title: str,
    goal: str,
    learner_profile: dict[str, Any] | None,
) -> Course:
    course = Course(
        owner_user_id=owner_user_id,
        intake_session_id=intake_session_id,
        title=title,
        goal=goal,
        learner_profile=learner_profile,
    )
    session.add(course)
    await session.flush()
    return course


async def add_lecture(
    session: AsyncSession,
    *,
    course_id: UUID,
    position: int,
    title: str,
    summary: str,
    topics: list[str],
) -> Lecture:
    lecture = Lecture(
        course_id=course_id, position=position, title=title, summary=summary, topics=topics
    )
    session.add(lecture)
    return lecture


async def get_course(session: AsyncSession, course_id: UUID) -> Course | None:
    return await session.get(Course, course_id)


async def list_lectures(session: AsyncSession, course_id: UUID) -> list[Lecture]:
    result = await session.execute(
        select(Lecture).where(Lecture.course_id == course_id).order_by(Lecture.position)
    )
    return list(result.scalars().all())


async def list_courses(session: AsyncSession, owner_user_id: UUID) -> list[Course]:
    result = await session.execute(
        select(Course)
        .where(Course.owner_user_id == owner_user_id)
        .order_by(Course.created_at.desc())
    )
    return list(result.scalars().all())


# --- Lectures & Docs ------------------------------------------------------


async def get_lecture(session: AsyncSession, lecture_id: UUID) -> Lecture | None:
    return await session.get(Lecture, lecture_id)


async def add_doc(
    session: AsyncSession, *, lecture_id: UUID, position: int, title: str, content: str
) -> Doc:
    doc = Doc(lecture_id=lecture_id, position=position, title=title, content=content)
    session.add(doc)
    return doc


async def list_docs(session: AsyncSession, lecture_id: UUID) -> list[Doc]:
    result = await session.execute(
        select(Doc).where(Doc.lecture_id == lecture_id).order_by(Doc.position)
    )
    return list(result.scalars().all())


async def list_recent_user_docs(
    session: AsyncSession, owner_user_id: UUID, limit: int = 6
) -> list[Doc]:
    """The learner's most recently generated lesson docs, across all their courses.

    Used to build the Daily Dino Dash from material they've actually studied.
    """
    result = await session.execute(
        select(Doc)
        .join(Lecture, Lecture.id == Doc.lecture_id)
        .join(Course, Course.id == Lecture.course_id)
        .where(Course.owner_user_id == owner_user_id)
        .order_by(Doc.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def add_reference(
    session: AsyncSession, *, lecture_id: UUID, position: int, type: str, url: str, title: str
) -> Reference:
    reference = Reference(lecture_id=lecture_id, position=position, type=type, url=url, title=title)
    session.add(reference)
    return reference


async def list_references(session: AsyncSession, lecture_id: UUID) -> list[Reference]:
    result = await session.execute(
        select(Reference).where(Reference.lecture_id == lecture_id).order_by(Reference.position)
    )
    return list(result.scalars().all())


def to_doc_view(doc: Doc) -> DocView:
    return DocView(id=doc.id, position=doc.position, title=doc.title, content=doc.content)


def to_reference_view(reference: Reference) -> ReferenceView:
    return ReferenceView(
        id=reference.id, type=reference.type, url=reference.url, title=reference.title
    )


# --- Quiz & lesson progress -----------------------------------------------


async def get_quiz(session: AsyncSession, lecture_id: UUID, topic_index: int) -> Quiz | None:
    result = await session.execute(
        select(Quiz).where(Quiz.lecture_id == lecture_id, Quiz.topic_index == topic_index)
    )
    return result.scalar_one_or_none()


async def add_quiz(
    session: AsyncSession, *, lecture_id: UUID, topic_index: int, questions: list[dict[str, Any]]
) -> Quiz:
    quiz = Quiz(lecture_id=lecture_id, topic_index=topic_index, questions=questions)
    session.add(quiz)
    await session.flush()
    return quiz


async def get_lesson_progress(
    session: AsyncSession, user_id: UUID, lecture_id: UUID, topic_index: int
) -> LessonProgress | None:
    result = await session.execute(
        select(LessonProgress).where(
            LessonProgress.user_id == user_id,
            LessonProgress.lecture_id == lecture_id,
            LessonProgress.topic_index == topic_index,
        )
    )
    return result.scalar_one_or_none()


async def record_quiz_score(
    session: AsyncSession, *, user_id: UUID, lecture_id: UUID, topic_index: int, score: int
) -> LessonProgress:
    progress = await get_lesson_progress(session, user_id, lecture_id, topic_index)
    passed_now = score >= 80
    if progress is None:
        progress = LessonProgress(
            user_id=user_id,
            lecture_id=lecture_id,
            topic_index=topic_index,
            best_score=score,
            passed=passed_now,
            attempts=1,
        )
        session.add(progress)
    else:
        progress.best_score = max(progress.best_score, score)
        progress.passed = progress.passed or passed_now
        progress.attempts += 1
    await session.flush()
    return progress


async def list_lesson_progress_for_course(
    session: AsyncSession, user_id: UUID, course_id: UUID
) -> list[LessonProgress]:
    result = await session.execute(
        select(LessonProgress)
        .join(Lecture, Lecture.id == LessonProgress.lecture_id)
        .where(Lecture.course_id == course_id, LessonProgress.user_id == user_id)
    )
    return list(result.scalars().all())
