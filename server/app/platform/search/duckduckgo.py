"""Keyless web/video search via DuckDuckGo (`ddgs`).

`ddgs` is synchronous, so calls run in a worker thread. Failures (rate limits,
network) are swallowed into an empty list — reference curation is best-effort,
never blocks lecture generation.
"""

import asyncio

from ddgs import DDGS
from loguru import logger

from app.shared.contracts.search import SearchKind, SearchResult


class DuckDuckGoSearchProvider:
    async def search(self, query: str, *, kind: SearchKind, max_results: int) -> list[SearchResult]:
        return await asyncio.to_thread(self._search_sync, query, kind, max_results)

    def _search_sync(self, query: str, kind: SearchKind, max_results: int) -> list[SearchResult]:
        try:
            ddgs = DDGS()
            if kind == "video":
                rows = ddgs.videos(query, max_results=max_results)
                return [
                    SearchResult(title=row.get("title", ""), url=row["content"])
                    for row in rows
                    if row.get("content")
                ]
            rows = ddgs.text(query, max_results=max_results)
            return [
                SearchResult(title=row.get("title", ""), url=row["href"])
                for row in rows
                if row.get("href")
            ]
        except Exception as exc:  # best-effort: never break generation on search failure
            logger.bind(query=query, kind=kind).warning(f"web search failed: {exc}")
            return []
