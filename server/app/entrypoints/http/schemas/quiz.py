"""Quiz request schemas."""

from pydantic import BaseModel


class QuizAttemptRequest(BaseModel):
    """The learner's chosen option index per question, in order."""

    answers: list[int]
