"""HTTP middleware."""

from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.runtime.request_context import set_request_id

REQUEST_ID_HEADER = "X-Request-ID"


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Establishes per-request context and echoes the request id back.

    Honours an inbound `X-Request-ID` (so a gateway/client can supply one),
    otherwise generates it. The id is available via `get_request_id()` for
    log correlation throughout the request.
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = set_request_id(request.headers.get(REQUEST_ID_HEADER))
        response = await call_next(request)
        response.headers[REQUEST_ID_HEADER] = request_id
        return response
