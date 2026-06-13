"""Request schema for the in-lesson tutor ("Ask DynoDoc")."""

from pydantic import BaseModel

from app.domains.course.dtos import TutorTurn


class AskRequest(BaseModel):
    """A learner's question plus the short conversation so far (client-held)."""

    question: str
    history: list[TutorTurn] = []
