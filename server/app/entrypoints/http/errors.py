"""Maps exceptions to RFC 9457 `problem+json` responses.

This is the one place HTTP status codes are derived from domain errors, so
domains stay transport-agnostic.
"""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.entrypoints.http.schemas.problem import FieldError, ProblemDetail
from app.shared.errors import AppError

PROBLEM_CONTENT_TYPE = "application/problem+json"


def _problem_response(problem: ProblemDetail) -> JSONResponse:
    return JSONResponse(
        status_code=problem.status,
        content=problem.model_dump(exclude_none=True),
        media_type=PROBLEM_CONTENT_TYPE,
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        return _problem_response(
            ProblemDetail(
                type=f"https://dynodoc.app/errors/{exc.code}",
                title=exc.message,
                status=exc.status_code,
                code=exc.code,
                instance=request.url.path,
            )
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return _problem_response(
            ProblemDetail(
                type="https://dynodoc.app/errors/validation_error",
                title="Validation failed",
                status=422,
                code="validation_error",
                instance=request.url.path,
                errors=[
                    FieldError(
                        field=".".join(str(part) for part in err["loc"]),
                        message=err["msg"],
                    )
                    for err in exc.errors()
                ],
            )
        )
