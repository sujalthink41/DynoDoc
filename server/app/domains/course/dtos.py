"""DTOs for the course domain's intake flow."""

from datetime import datetime
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
    """The AI's structured reply each turn of the onboarding conversation."""

    on_topic: bool = True  # is the request about learning a technical/tech subject?
    is_complete: bool = False  # enough context gathered to build a learner profile?
    message: str = ""  # the assistant's single conversational reply this turn
    profile: LearnerProfile | None = None


class TranscriptTurn(BaseModel):
    """One message in an intake conversation (for live chat + read-only history)."""

    role: str  # "user" | "assistant"
    content: str


class IntakeSessionView(BaseModel):
    """What the API returns for an intake session."""

    id: UUID
    status: str
    goal: str
    transcript: list[TranscriptTurn]
    profile: LearnerProfile | None


class IntakeSummary(BaseModel):
    """Lightweight shape for the chat-history sidebar."""

    id: UUID
    goal: str
    status: str
    created_at: datetime


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
    lessons_total: int
    lessons_passed: int


class CourseView(BaseModel):
    id: UUID
    title: str
    goal: str
    status: str
    completion_percent: int
    average_score: int
    lectures: list[LectureView]


class CourseSummary(BaseModel):
    """Lightweight shape for the 'my courses' list."""

    id: UUID
    title: str
    goal: str
    status: str
    completion_percent: int
    average_score: int


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


class LessonState(BaseModel):
    """Per-topic state for the lecture sidebar (lock / done / score)."""

    index: int
    topic: str
    generated: bool
    unlocked: bool
    attempted: bool
    passed: bool
    mastered: bool  # best score == 100
    score: int


class LectureDetailView(BaseModel):
    id: UUID
    position: int
    title: str
    summary: str
    status: str
    course_id: UUID
    course_title: str
    lessons: list[LessonState]
    docs: list[DocView]
    references: list[ReferenceView]


# --- Quiz -----------------------------------------------------------------


class QuizQuestion(BaseModel):
    """Stored / quiz-writer shape — includes the correct answer."""

    question: str
    options: list[str]
    answer_index: int


class QuizSpec(BaseModel):
    """The quiz-writer agent's structured output."""

    questions: list[QuizQuestion]


class QuizQuestionView(BaseModel):
    """Client shape — the answer is never sent to the browser."""

    question: str
    options: list[str]


class QuizView(BaseModel):
    lecture_id: UUID
    topic_index: int
    questions: list[QuizQuestionView]
    best_score: int
    mastered: bool  # best score == 100 → locked, read-only review
    # Correct option per question — populated ONLY when mastered (review mode).
    answers: list[int] | None = None


class QuizResultItem(BaseModel):
    correct: bool  # was the learner's chosen answer correct
    # The correct option — revealed ONLY once the lesson is mastered (100%).
    answer_index: int | None = None


class QuizResult(BaseModel):
    score: int
    passed: bool
    total: int
    correct_count: int
    mastered: bool  # best score is now 100
    can_retake: bool  # may attempt again (only while not mastered)
    results: list[QuizResultItem]
    unlocked_next: bool
