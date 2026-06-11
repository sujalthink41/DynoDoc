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


# --- Course generation ----------------------------------------------------


class RoadmapLecture(BaseModel):
    """One lecture as proposed by the architect step."""

    title: str
    summary: str
    topics: list[str]


class Roadmap(BaseModel):
    """The architect's structured output: a course title + ordered lectures."""

    title: str
    lectures: list[RoadmapLecture]


class LectureView(BaseModel):
    id: UUID
    position: int
    title: str
    summary: str
    topics: list[str]
    status: str


class CourseView(BaseModel):
    id: UUID
    title: str
    goal: str
    status: str
    lectures: list[LectureView]


class CourseSummary(BaseModel):
    """Lightweight shape for the 'my courses' list."""

    id: UUID
    title: str
    goal: str
    status: str


# --- Lecture content (writer step) ----------------------------------------


class DocDraft(BaseModel):
    """A writer agent's structured output: one lesson doc (Markdown)."""

    title: str
    content: str


class DocView(BaseModel):
    id: UUID
    position: int
    title: str
    content: str


class ReferenceView(BaseModel):
    id: UUID
    type: str
    url: str
    title: str


class LectureDetailView(BaseModel):
    id: UUID
    position: int
    title: str
    summary: str
    topics: list[str]
    status: str
    docs: list[DocView]
    references: list[ReferenceView]
