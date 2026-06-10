"""Signed-cookie session helpers.

The session lives in a signed cookie (Starlette SessionMiddleware). We store the
authenticated `Principal` plus a CSRF token. Nothing sensitive is exposed to JS:
the cookie is httpOnly and signed, and the CSRF token guards mutations.
"""

from secrets import token_urlsafe
from typing import Any

from pydantic import BaseModel, ValidationError

from app.domains.user.dtos import Principal


class SessionData(BaseModel):
    principal: Principal
    csrf_token: str


def write_session(session: dict[str, Any], principal: Principal) -> SessionData:
    """Store the principal + a fresh CSRF token in the session cookie."""
    data = SessionData(principal=principal, csrf_token=token_urlsafe(32))
    session["principal"] = data.principal.model_dump(mode="json")
    session["csrf"] = data.csrf_token
    return data


def read_session(session: dict[str, Any]) -> SessionData | None:
    """Parse the session cookie back into SessionData, or None if absent/invalid."""
    principal_data = session.get("principal")
    csrf = session.get("csrf")
    if not isinstance(principal_data, dict) or not isinstance(csrf, str) or not csrf:
        return None
    try:
        principal = Principal.model_validate(principal_data)
    except ValidationError:
        return None
    return SessionData(principal=principal, csrf_token=csrf)


def clear_session(session: dict[str, Any]) -> None:
    session.clear()
