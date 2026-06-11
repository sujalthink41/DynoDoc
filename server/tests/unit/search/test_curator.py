"""Unit: SearchResourceCurator turns search results into typed references."""

from app.platform.search.curator import SearchResourceCurator
from app.shared.contracts.search import SearchResult
from tests.fixtures.fakes import FakeSearchProvider


async def test_maps_web_and_video_results_to_references() -> None:
    provider = FakeSearchProvider(
        web=[
            SearchResult(title="Real Python: Decorators", url="https://realpython.com/x"),
            SearchResult(title="Docs", url="https://docs.python.org/y"),
        ],
        video=[SearchResult(title="Decorators explained", url="https://youtube.com/watch?v=1")],
    )
    curator = SearchResourceCurator(provider, max_articles=4, max_videos=2)

    refs = await curator.find_references(
        lecture_title="Decorators", summary="...", topics=["decorators"]
    )

    types = [r.type for r in refs]
    assert types.count("article") == 2
    assert types.count("youtube") == 1
    assert all(r.url.startswith("http") for r in refs)
