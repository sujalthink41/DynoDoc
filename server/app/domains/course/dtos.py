"""DTOs for the course domain's intake flow."""

from uuid import UUID

from pydantic import BaseModel


class LearnerProfile(BaseModel):
    """What the intake conversation distils about the learner."""

    experience_level: str
    background: str
    goal: str
    weekly_time: str
    notes: str = ""


class IntakeStep(BaseModel):
    """The AI's structured answer each turn: more questions, or a final profile."""

    is_complete: bool
    questions: list[str] = []
    profile: LearnerProfile | None = None


class IntakeSessionView(BaseModel):
    """What the API returns for an intake session."""

    id: UUID
    status: str
    goal: str
    questions: list[str]
    profile: LearnerProfile | None
