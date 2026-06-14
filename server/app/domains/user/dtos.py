"""Pydantic DTOs for the user domain (transport/serialization shapes)."""

from uuid import UUID

from pydantic import BaseModel, EmailStr


class Principal(BaseModel):
    """The authenticated identity carried in the session cookie."""

    id: UUID
    subject: str
    email: EmailStr
    display_name: str | None = None


class UserProfile(BaseModel):
    """A user's public-ish profile shape (used by /me and profile pages)."""

    id: UUID
    email: EmailStr
    display_name: str | None
    avatar_url: str | None
    is_active: bool


class PersonaQuestionView(BaseModel):
    key: str
    prompt: str
    emoji: str
    kind: str  # "choice" | "text"
    options: list[str]
    allow_custom: bool
    answer: str


class PersonaView(BaseModel):
    """The 'about you' questionnaire with the learner's answers + completion."""

    questions: list[PersonaQuestionView]
    answered: int
    total: int
    percent: int
