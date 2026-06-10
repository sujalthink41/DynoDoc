"""Google OAuth (OpenID Connect) via authlib's Starlette integration.

`begin_login` redirects to Google's consent screen; `complete_login` handles the
callback, exchanges the code, and returns a `GoogleIdentity`. Configuration is
read from settings; if the client id/secret are missing we fail with a clear 503.
"""

from functools import lru_cache
from typing import Any, cast

from authlib.integrations.starlette_client import OAuth, OAuthError
from starlette.requests import Request
from starlette.responses import RedirectResponse

from app.runtime.settings import get_settings
from app.shared.contracts.identity import GoogleIdentity
from app.shared.errors import AppError, DependencyUnavailableError

_SCOPES = "openid email profile"


@lru_cache
def _registry() -> Any:
    settings = get_settings()
    if not settings.google_client_id or not settings.google_client_secret:
        raise DependencyUnavailableError("Google OAuth is not configured", code="oauth_unavailable")
    oauth = OAuth()
    oauth.register(
        name="google",
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": _SCOPES},
    )
    return oauth


def _client() -> Any:
    client = _registry().create_client("google")
    if client is None:
        raise DependencyUnavailableError("Google OAuth is not configured", code="oauth_unavailable")
    return client


def _field(profile: object, key: str) -> str:
    if not isinstance(profile, dict):
        return ""
    value = profile.get(key)
    return value if isinstance(value, str) else ""


async def begin_login(request: Request, redirect_uri: str) -> RedirectResponse:
    response = await _client().authorize_redirect(request, redirect_uri)
    return cast(RedirectResponse, response)


async def complete_login(request: Request) -> GoogleIdentity:
    try:
        token = await _client().authorize_access_token(request)
    except OAuthError as exc:
        raise AppError(
            f"OAuth exchange failed: {exc.error}",
            code="oauth_exchange_failed",
            status_code=400,
        ) from exc

    profile = token.get("userinfo")
    if profile is None:
        profile = await _client().userinfo(token=token)

    return GoogleIdentity(
        subject=_field(profile, "sub") or _field(profile, "email"),
        email=_field(profile, "email"),
        name=_field(profile, "name") or None,
        picture=_field(profile, "picture") or None,
    )
