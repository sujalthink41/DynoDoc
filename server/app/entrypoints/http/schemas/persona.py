"""Request schema for updating the 'about you' persona."""

from pydantic import BaseModel


class PersonaUpdateRequest(BaseModel):
    """A partial map of question_key → answer; unknown keys are ignored."""

    answers: dict[str, str]
