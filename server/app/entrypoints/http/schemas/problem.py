"""RFC 9457 `problem+json` response model — the single error shape for the API."""

from pydantic import BaseModel


class FieldError(BaseModel):
    field: str
    message: str


class ProblemDetail(BaseModel):
    type: str = "about:blank"
    title: str
    status: int
    detail: str | None = None
    instance: str | None = None
    errors: list[FieldError] | None = None
