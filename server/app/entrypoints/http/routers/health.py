"""Liveness probe. Thin router: no business logic."""

from fastapi import APIRouter, Depends

from app.entrypoints.http.schemas.health import HealthResponse
from app.runtime.settings import Settings, get_settings

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse, summary="Liveness probe")
async def health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        version=settings.version,
        environment=settings.environment,
    )
