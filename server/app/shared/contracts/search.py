"""SearchProvider port — real web/video search behind an interface.

Default adapter is keyless DuckDuckGo; swappable for Brave/Exa/etc. later.
"""

from typing import Literal, Protocol

from pydantic import BaseModel

SearchKind = Literal["web", "video"]


class SearchResult(BaseModel):
    title: str
    url: str


class SearchProvider(Protocol):
    async def search(
        self, query: str, *, kind: SearchKind, max_results: int
    ) -> list[SearchResult]: ...
