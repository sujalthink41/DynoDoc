"""Course-domain persistence (plain async functions over an AsyncSession)."""

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.course.dtos import (
    CourseSummary,
    CourseView,
    DocView,
    IntakeSessionView,
    LearnerProfile,
    LectureDetailView,
    LectureView,
    ReferenceView,
)
from app.domains.course.models import Course, Doc, IntakeSession, Lecture, Reference


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


def to_view(intake: IntakeSession) -> IntakeSessionView:
    return IntakeSessionView(
        id=intake.id,
        status=intake.status,
        goal=intake.goal,
        questions=intake.pending_questions,
        profile=LearnerProfile(**intake.profile) if intake.profile else None,
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


def to_lecture_view(lecture: Lecture) -> LectureView:
    return LectureView(
        id=lecture.id,
        position=lecture.position,
        title=lecture.title,
        summary=lecture.summary,
        topics=lecture.topics,
        status=lecture.status,
    )


def to_course_view(course: Course, lectures: list[Lecture]) -> CourseView:
    return CourseView(
        id=course.id,
        title=course.title,
        goal=course.goal,
        status=course.status,
        lectures=[to_lecture_view(lecture) for lecture in lectures],
    )


def to_course_summary(course: Course) -> CourseSummary:
    return CourseSummary(id=course.id, title=course.title, goal=course.goal, status=course.status)


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


def to_lecture_detail_view(
    lecture: Lecture, docs: list[Doc], references: list[Reference]
) -> LectureDetailView:
    return LectureDetailView(
        id=lecture.id,
        position=lecture.position,
        title=lecture.title,
        summary=lecture.summary,
        topics=lecture.topics,
        status=lecture.status,
        docs=[to_doc_view(doc) for doc in docs],
        references=[to_reference_view(ref) for ref in references],
    )
