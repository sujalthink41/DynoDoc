"""Intake routes — start an onboarding conversation and answer its questions."""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.course.dtos import IntakeSessionView
from app.domains.course.repository import get_intake_session, to_view
from app.domains.course.service import IntakeService
from app.domains.user.models import User
from app.entrypoints.http.deps import db_session, get_text_generator, require_principal
from app.entrypoints.http.schemas.intake import AnswerRequest, StartIntakeRequest
from app.shared.contracts.llm import TextGenerator
from app.shared.errors import NotFoundError

router = APIRouter(prefix="/intake", tags=["intake"])


@router.post("", response_model=IntakeSessionView, status_code=status.HTTP_201_CREATED)
async def start_intake(
    body: StartIntakeRequest,
    user: User = Depends(require_principal),
    session: AsyncSession = Depends(db_session),
    generator: TextGenerator = Depends(get_text_generator),
) -> IntakeSessionView:
    intake = await IntakeService(generator).start(session, owner_user_id=user.id, goal=body.goal)
    return to_view(intake)


@router.post("/{intake_id}/answer", response_model=IntakeSessionView)
async def answer_intake(
    intake_id: UUID,
    body: AnswerRequest,
    user: User = Depends(require_principal),
    session: AsyncSession = Depends(db_session),
    generator: TextGenerator = Depends(get_text_generator),
) -> IntakeSessionView:
    intake = await get_intake_session(session, intake_id)
    if intake is None or intake.owner_user_id != user.id:
        raise NotFoundError("Intake session not found", code="intake_not_found")
    intake = await IntakeService(generator).answer(session, intake=intake, answer=body.answer)
    return to_view(intake)


@router.get("/{intake_id}", response_model=IntakeSessionView)
async def get_intake(
    intake_id: UUID,
    user: User = Depends(require_principal),
    session: AsyncSession = Depends(db_session),
) -> IntakeSessionView:
    intake = await get_intake_session(session, intake_id)
    if intake is None or intake.owner_user_id != user.id:
        raise NotFoundError("Intake session not found", code="intake_not_found")
    return to_view(intake)
