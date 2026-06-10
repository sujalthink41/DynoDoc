"""Auth routes. Thin: orchestrate the OAuth adapter, persistence, and session."""

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import RedirectResponse
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.user.dtos import Principal
from app.domains.user.repository import get_or_create_oauth_user, to_principal
from app.entrypoints.http.deps import db_session
from app.entrypoints.http.schemas.auth import DevLoginRequest
from app.platform.auth import google_oauth
from app.platform.auth.session import clear_session, write_session
from app.runtime.settings import Settings, get_settings
from app.shared.contracts.identity import GoogleIdentity

router = APIRouter(prefix="/auth", tags=["auth"])

# Dev/test only — registered separately so it never ships to production.
dev_router = APIRouter(prefix="/auth", tags=["auth-dev"])


@router.get("/google/login")
async def google_login(
    request: Request, settings: Settings = Depends(get_settings)
) -> RedirectResponse:
    return await google_oauth.begin_login(request, settings.google_redirect_uri)


@router.get("/google/callback")
async def google_callback(
    request: Request,
    session: AsyncSession = Depends(db_session),
    settings: Settings = Depends(get_settings),
) -> RedirectResponse:
    identity = await google_oauth.complete_login(request)
    user, is_new = await get_or_create_oauth_user(session, identity=identity)
    write_session(request.session, to_principal(user))
    logger.bind(user_id=str(user.id), is_new=is_new).info("user signed in via google")
    return RedirectResponse(
        url=settings.frontend_post_login_url, status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(request: Request) -> Response:
    clear_session(request.session)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@dev_router.post("/dev-login")
async def dev_login(
    body: DevLoginRequest,
    request: Request,
    session: AsyncSession = Depends(db_session),
) -> Principal:
    identity = GoogleIdentity(subject=f"dev:{body.email}", email=str(body.email), name=body.name)
    user, is_new = await get_or_create_oauth_user(session, identity=identity)
    principal = to_principal(user)
    write_session(request.session, principal)
    logger.bind(user_id=str(user.id), is_new=is_new).info("user signed in via dev-login")
    return principal
