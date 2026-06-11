"""ResourceCurator port — finds real learning links for a lecture's topics.

The real adapter uses an ADK agent with the `google_search` tool (Gemini), so
the links come from actual web search (not hallucinated). Tests use a fake.
"""

from typing import Protocol

from pydantic import BaseModel


class ReferenceDraft(BaseModel):
    type: str  # "article" | "youtube"
    url: str
    title: str


class ResourceCurator(Protocol):
    async def find_references(
        self, *, lecture_title: str, summary: str, topics: list[str]
    ) -> list[ReferenceDraft]: ...
