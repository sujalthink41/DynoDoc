"""Intake request schemas."""

from pydantic import BaseModel, Field


class StartIntakeRequest(BaseModel):
    goal: str = Field(min_length=1, max_length=500)


class AnswerRequest(BaseModel):
    answer: str = Field(min_length=1)
