import asyncio
from langchain_community.tools import DuckDuckGoSearchRun

_search = DuckDuckGoSearchRun()


def search_web(query: str) -> str:
    """Run a DuckDuckGo search synchronously and return the result string."""
    return _search.run(query)


async def search_web_async(query: str) -> str:
    """Async wrapper — runs the blocking search in a thread pool."""
    return await asyncio.to_thread(search_web, query)
