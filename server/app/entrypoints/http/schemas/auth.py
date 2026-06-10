"""Auth request schemas."""

from pydantic import BaseModel, EmailStr


class DevLoginRequest(BaseModel):
    """Dev/test-only login: skips Google, logs in by email."""

    email: EmailStr
    name: str | None = None
