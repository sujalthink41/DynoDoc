"""ResourceCurator backed by a SearchProvider (no LLM — fast, free, no rate cost).

Runs a web search (articles) and a video search (YouTube) for the lecture's
topics and returns the top relevant results as references. Results are already
relevance-ranked by the provider; optional LLM re-ranking could be added later.
"""

from app.shared.contracts.curation import ReferenceDraft
from app.shared.contracts.search import SearchProvider


class SearchResourceCurator:
    def __init__(
        self, provider: SearchProvider, *, max_articles: int = 4, max_videos: int = 2
    ) -> None:
        self._provider = provider
        self._max_articles = max_articles
        self._max_videos = max_videos

    async def find_references(
        self, *, lecture_title: str, summary: str, topics: list[str]
    ) -> list[ReferenceDraft]:
        topic_str = ", ".join(topics) if topics else lecture_title
        articles = await self._provider.search(
            f"{lecture_title} {topic_str} tutorial", kind="web", max_results=self._max_articles
        )
        videos = await self._provider.search(
            f"{lecture_title} {topic_str}", kind="video", max_results=self._max_videos
        )
        return [
            ReferenceDraft(type="article", url=result.url, title=result.title)
            for result in articles
        ] + [
            ReferenceDraft(type="youtube", url=result.url, title=result.title) for result in videos
        ]
