"""Per-request context propagated via contextvars.

Currently carries the request id (for log correlation across the request and
any work it triggers). The current-user context will be added with the auth
slice (0.1/0.2).
"""

from contextvars import ContextVar
from uuid import uuid4

_request_id: ContextVar[str] = ContextVar("request_id", default="")


def set_request_id(value: str | None) -> str:
    """Set the request id, generating one if not supplied. Returns the value."""
    request_id = value or uuid4().hex
    _request_id.set(request_id)
    return request_id


def get_request_id() -> str:
    return _request_id.get()
