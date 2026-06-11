"""Fakes for the EXTERNAL ports (the things we don't call for real in tests).

The database is not faked — persistence is tested against real SQLite.
"""

from collections.abc import AsyncGenerator
from typing import Any

from google.adk.models.base_llm import BaseLlm
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types
from pydantic import BaseModel, Field

from app.shared.contracts.curation import ReferenceDraft
from app.shared.contracts.llm import Message
from app.shared.contracts.search import SearchKind, SearchResult


class FakeTextGenerator:
    """Returns queued structured responses instead of calling a real LLM (intake)."""

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


class FakeLlm(BaseLlm):
    """Fakes ADK's model layer so agent pipelines run offline + deterministically.

    Each call returns the next queued text (e.g. a JSON object the agent's prompt
    asked for). Drop-in for a real LiteLlm in `LlmAgent(model=...)`.
    """

    model: str = "fake"
    responses: list[str] = Field(default_factory=list)

    async def generate_content_async(
        self, llm_request: LlmRequest, stream: bool = False
    ) -> AsyncGenerator[LlmResponse]:
        text = self.responses.pop(0) if self.responses else "{}"
        yield LlmResponse(content=types.Content(role="model", parts=[types.Part(text=text)]))


class FakeResourceCurator:
    """Returns canned references instead of searching the web."""

    def __init__(self) -> None:
        self.references: list[ReferenceDraft] = []

    async def find_references(
        self, *, lecture_title: str, summary: str, topics: list[str]
    ) -> list[ReferenceDraft]:
        return list(self.references)


class FakeSearchProvider:
    """Returns canned search results per kind (for testing the curator logic)."""

    def __init__(
        self, web: list[SearchResult] | None = None, video: list[SearchResult] | None = None
    ) -> None:
        self._web = web or []
        self._video = video or []

    async def search(self, query: str, *, kind: SearchKind, max_results: int) -> list[SearchResult]:
        return (self._video if kind == "video" else self._web)[:max_results]
