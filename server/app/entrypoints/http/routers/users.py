"""User-facing routes (the current user's profile + learning stats)."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.gamification.dtos import ProfileStatsView
from app.domains.user import persona as persona_catalog
from app.domains.user.dtos import PersonaView, UserProfile
from app.domains.user.models import User
from app.domains.user.repository import get_or_create_persona, save_persona
from app.entrypoints.http.deps import db_session, require_principal
from app.entrypoints.http.schemas.persona import PersonaUpdateRequest
from app.processes.profile.stats import build_profile_stats

router = APIRouter(tags=["user"])


@router.get("/me", response_model=UserProfile, summary="The current user")
async def me(user: User = Depends(require_principal)) -> UserProfile:
    return UserProfile(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        avatar_url=user.avatar_url,
        is_active=user.is_active,
    )


@router.get("/me/stats", response_model=ProfileStatsView, summary="The current user's stats")
async def my_stats(
    user: User = Depends(require_principal),
    session: AsyncSession = Depends(db_session),
) -> ProfileStatsView:
    return await build_profile_stats(session, user_id=user.id)


@router.get("/me/persona", response_model=PersonaView, summary="The 'about you' questionnaire")
async def get_my_persona(
    user: User = Depends(require_principal),
    session: AsyncSession = Depends(db_session),
) -> PersonaView:
    persona = await get_or_create_persona(session, user.id)
    return persona_catalog.build_view(persona.answers)


@router.put("/me/persona", response_model=PersonaView, summary="Update 'about you' answers")
async def update_my_persona(
    body: PersonaUpdateRequest,
    user: User = Depends(require_principal),
    session: AsyncSession = Depends(db_session),
) -> PersonaView:
    persona = await save_persona(session, user.id, body.answers)
    return persona_catalog.build_view(persona.answers)
