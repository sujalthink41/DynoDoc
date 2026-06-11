"""Course-domain persistence (plain async functions over an AsyncSession)."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.course.dtos import IntakeSessionView, LearnerProfile
from app.domains.course.models import IntakeSession


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
