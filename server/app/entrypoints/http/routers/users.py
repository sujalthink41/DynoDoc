"""User-facing routes (the current user's profile)."""

from fastapi import APIRouter, Depends

from app.domains.user.dtos import UserProfile
from app.domains.user.models import User
from app.entrypoints.http.deps import require_principal

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
