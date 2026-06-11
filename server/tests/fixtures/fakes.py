"""Fakes for the EXTERNAL ports (the things we don't call for real in tests).

The database is not faked — persistence is tested against real SQLite.
"""

from typing import Any

from pydantic import BaseModel

from app.shared.contracts.llm import Message


class FakeTextGenerator:
    """Returns queued structured responses instead of calling a real LLM."""

    def __init__(self) -> None:
        self.responses: list[BaseModel] = []
        self.calls: list[list[Message]] = []

    def queue(self, response: BaseModel) -> None:
        self.responses.append(response)

    async def generate_structured(self, messages: list[Message], *, schema: type[BaseModel]) -> Any:
        self.calls.append(messages)
        if not self.responses:
            raise AssertionError("FakeTextGenerator has no queued response")
        return self.responses.pop(0)
