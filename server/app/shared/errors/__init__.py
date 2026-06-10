"""Base application error taxonomy.

Domains raise these; the HTTP layer maps them to RFC 9457 `problem+json`
responses (see `app/entrypoints/http/errors.py`). Keeping the taxonomy here
means no domain needs to know anything about HTTP.
"""


class AppError(Exception):
    """Base class for all expected application/domain errors."""

    status_code: int = 500
    title: str = "Internal Server Error"
    error_type: str = "about:blank"

    def __init__(self, detail: str | None = None) -> None:
        self.detail = detail or self.title
        super().__init__(self.detail)


class NotFoundError(AppError):
    status_code = 404
    title = "Resource Not Found"
    error_type = "https://dynodoc.app/errors/not-found"


class ConflictError(AppError):
    status_code = 409
    title = "Conflict"
    error_type = "https://dynodoc.app/errors/conflict"


class PermissionDeniedError(AppError):
    status_code = 403
    title = "Permission Denied"
    error_type = "https://dynodoc.app/errors/permission-denied"


class UnauthorizedError(AppError):
    status_code = 401
    title = "Unauthorized"
    error_type = "https://dynodoc.app/errors/unauthorized"
