"""Course routes — generate a roadmap from a completed intake, then read it."""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from google.adk.models.base_llm import BaseLlm
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.course.dtos import CourseSummary, CourseView
from app.domains.course.progress import build_course_summary, build_course_view
from app.domains.course.repository import (
    get_course,
    get_intake_session,
    list_courses,
)
from app.domains.user.models import User
from app.entrypoints.http.deps import db_session, get_llm_model, require_principal
from app.entrypoints.http.schemas.course import CreateCourseRequest
from app.processes.course_generation.pipeline import generate_course
from app.shared.errors import AppError, NotFoundError

router = APIRouter(prefix="/courses", tags=["courses"])


@router.post("", response_model=CourseView, status_code=status.HTTP_201_CREATED)
async def create_course_route(
    body: CreateCourseRequest,
    user: User = Depends(require_principal),
    session: AsyncSession = Depends(db_session),
    model: BaseLlm = Depends(get_llm_model),
) -> CourseView:
    intake = await get_intake_session(session, body.intake_id)
    if intake is None or intake.owner_user_id != user.id:
        raise NotFoundError("Intake session not found", code="intake_not_found")
    if intake.status != "ready" or not intake.profile:
        raise AppError("Intake is not complete yet", code="intake_not_ready", status_code=409)

    course = await generate_course(
        session,
        model=model,
        owner_user_id=user.id,
        intake_session_id=intake.id,
        goal=intake.goal,
        profile=intake.profile,
    )
    return await build_course_view(session, user_id=user.id, course=course)


@router.get("", response_model=list[CourseSummary])
async def list_my_courses(
    user: User = Depends(require_principal),
    session: AsyncSession = Depends(db_session),
) -> list[CourseSummary]:
    courses = await list_courses(session, user.id)
    return [
        await build_course_summary(session, user_id=user.id, course=course) for course in courses
    ]


@router.get("/{course_id}", response_model=CourseView)
async def get_course_route(
    course_id: UUID,
    user: User = Depends(require_principal),
    session: AsyncSession = Depends(db_session),
) -> CourseView:
    course = await get_course(session, course_id)
    if course is None or course.owner_user_id != user.id:
        raise NotFoundError("Course not found", code="course_not_found")
    return await build_course_view(session, user_id=user.id, course=course)
