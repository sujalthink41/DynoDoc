"""HTTP middleware."""

import time
from collections.abc import Awaitable, Callable

from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.runtime.request_context import set_request_id

REQUEST_ID_HEADER = "X-Request-ID"


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Establishes per-request context, logs the request, and echoes the id back.

    Honours an inbound `X-Request-ID` (so a gateway/client can supply one),
    otherwise generates it. The id is on `get_request_id()` and is auto-injected
    into every log line for the request, so logs are correlatable.
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = set_request_id(request.headers.get(REQUEST_ID_HEADER))
        started = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            duration_ms = round((time.perf_counter() - started) * 1000, 2)
            logger.bind(
                method=request.method,
                path=request.url.path,
                duration_ms=duration_ms,
            ).exception("request failed")
            raise

        duration_ms = round((time.perf_counter() - started) * 1000, 2)
        response.headers[REQUEST_ID_HEADER] = request_id
        logger.bind(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
        ).info(f"{request.method} {request.url.path} {response.status_code} {duration_ms}ms")
        return response
