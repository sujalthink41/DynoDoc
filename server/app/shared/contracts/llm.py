"""TextGenerator port — the LLM behind an interface.

`generate_structured` forces the model to return a typed Pydantic object (not
free text), which is what makes AI output safe to consume and easy to test. The
real adapter (Gemini) lives in platform/; tests use a fake.
"""

from typing import Protocol, TypeVar

from pydantic import BaseModel


class Message(BaseModel):
    role: str  # "system" | "user" | "assistant"
    content: str


SchemaT = TypeVar("SchemaT", bound=BaseModel)


class TextGenerator(Protocol):
    async def generate_structured(
        self, messages: list[Message], *, schema: type[SchemaT]
    ) -> SchemaT: ...
