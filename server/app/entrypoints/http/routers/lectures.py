"""Lecture routes — read a lecture, generate one topic at a time, fetch links."""

from uuid import UUID

from fastapi import APIRouter, Depends
from google.adk.models.base_llm import BaseLlm
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.course.dtos import LectureDetailView
from app.domains.course.models import Lecture
from app.domains.course.repository import (
    get_course,
    get_lecture,
    list_docs,
    list_references,
    to_lecture_detail_view,
)
from app.domains.user.models import User
from app.entrypoints.http.deps import (
    db_session,
    get_llm_model,
    get_resource_curator,
    require_principal,
)
from app.processes.course_generation.curation import generate_lecture_references
from app.processes.course_generation.writer import generate_topic_doc
from app.shared.contracts.curation import ResourceCurator
from app.shared.errors import NotFoundError

router = APIRouter(prefix="/lectures", tags=["lectures"])


async def _load_owned_lecture(session: AsyncSession, lecture_id: UUID, user: User) -> Lecture:
    lecture = await get_lecture(session, lecture_id)
    if lecture is not None:
        course = await get_course(session, lecture.course_id)
        if course is not None and course.owner_user_id == user.id:
            return lecture
    raise NotFoundError("Lecture not found", code="lecture_not_found")


async def _detail(session: AsyncSession, lecture: Lecture) -> LectureDetailView:
    docs = await list_docs(session, lecture.id)
    references = await list_references(session, lecture.id)
    return to_lecture_detail_view(lecture, docs, references)


@router.get("/{lecture_id}", response_model=LectureDetailView)
async def get_lecture_route(
    lecture_id: UUID,
    user: User = Depends(require_principal),
    session: AsyncSession = Depends(db_session),
) -> LectureDetailView:
    lecture = await _load_owned_lecture(session, lecture_id, user)
    return await _detail(session, lecture)


@router.post("/{lecture_id}/topics/{topic_index}", response_model=LectureDetailView)
async def generate_topic_route(
    lecture_id: UUID,
    topic_index: int,
    user: User = Depends(require_principal),
    session: AsyncSession = Depends(db_session),
    model: BaseLlm = Depends(get_llm_model),
) -> LectureDetailView:
    lecture = await _load_owned_lecture(session, lecture_id, user)
    if topic_index < 0 or topic_index >= len(lecture.topics):
        raise NotFoundError("Topic not found", code="topic_not_found")

    docs = await list_docs(session, lecture.id)
    if any(doc.position == topic_index + 1 for doc in docs):  # already generated — idempotent
        return await _detail(session, lecture)

    course = await get_course(session, lecture.course_id)
    profile = (course.learner_profile if course else None) or {}
    await generate_topic_doc(
        session, model=model, lecture=lecture, topic_index=topic_index, profile=profile
    )

    docs = await list_docs(session, lecture.id)
    lecture.status = "ready" if len(docs) >= len(lecture.topics) else "in_progress"
    return await _detail(session, lecture)


@router.post("/{lecture_id}/references", response_model=LectureDetailView)
async def generate_references_route(
    lecture_id: UUID,
    user: User = Depends(require_principal),
    session: AsyncSession = Depends(db_session),
    curator: ResourceCurator = Depends(get_resource_curator),
) -> LectureDetailView:
    lecture = await _load_owned_lecture(session, lecture_id, user)
    if not await list_references(session, lecture.id):  # idempotent
        await generate_lecture_references(session, curator=curator, lecture=lecture)
    return await _detail(session, lecture)
