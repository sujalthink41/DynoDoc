"""Central application errors — defined ONCE, reused everywhere.

Domains/platform raise these with a machine-readable ``code``; they never define
their own error classes. The HTTP layer turns them into RFC 9457 `problem+json`
responses (see `app/entrypoints/http/errors.py`).

    raise NotFoundError("Course not found", code="course_not_found")
    raise AppError("Google OAuth not configured", code="oauth_unavailable", status_code=503)
"""


class AppError(Exception):
    def __init__(self, message: str, code: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code


class NotFoundError(AppError):
    def __init__(self, message: str, code: str = "not_found") -> None:
        super().__init__(message=message, code=code, status_code=404)


class ConflictError(AppError):
    def __init__(self, message: str, code: str = "conflict") -> None:
        super().__init__(message=message, code=code, status_code=409)


class ValidationError(AppError):
    def __init__(self, message: str, code: str = "validation_error") -> None:
        super().__init__(message=message, code=code, status_code=422)


class UnauthorizedError(AppError):
    def __init__(self, message: str, code: str = "not_authenticated") -> None:
        super().__init__(message=message, code=code, status_code=401)


class PermissionDeniedError(AppError):
    def __init__(self, message: str, code: str = "permission_denied") -> None:
        super().__init__(message=message, code=code, status_code=403)


class DependencyUnavailableError(AppError):
    """A required downstream dependency (DB, AI provider, sandbox) is unavailable."""

    def __init__(self, message: str, code: str = "dependency_unavailable") -> None:
        super().__init__(message=message, code=code, status_code=503)
