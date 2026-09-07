import asyncio
import os

import httpx
from ddgs import DDGS
from dotenv import load_dotenv

from tools.registry import tool

load_dotenv()

TAVILY_SEARCH_URL = "https://api.tavily.com/search"


async def _search_tavily(query: str) -> str:
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY not configured")

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(
            TAVILY_SEARCH_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={"query": query, "max_results": 5},
        )
    response.raise_for_status()
    results = response.json().get("results", [])

    if not results:
        return "No results found."

    return "\n\n".join(
        f"{i}. {result.get('title')} ({result.get('url')})\n{result.get('content')}"
        for i, result in enumerate(results, start=1)
    )


def _search_duckduckgo_sync(query: str) -> str:
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=5))

    if not results:
        return "No results found."

    return "\n\n".join(
        f"{i}. {result.get('title')} ({result.get('href')})\n{result.get('body')}"
        for i, result in enumerate(results, start=1)
    )


async def _search_duckduckgo(query: str) -> str:
    return await asyncio.to_thread(_search_duckduckgo_sync, query)


@tool(
    name="web_search",
    description=(
        "Search the web for current information on a topic. Returns a short "
        "list of relevant results with titles, URLs, and content snippets. "
        "Prefer provider='duckduckgo' (free) by default to save cost. Only "
        "use provider='tavily' (paid, higher-quality AI-optimized results) "
        "when the query needs more accurate or recent results, or when a "
        "duckduckgo search already came back empty or insufficient."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query to look up on the web.",
            },
            "provider": {
                "type": "string",
                "enum": ["duckduckgo", "tavily"],
                "description": (
                    "Which search provider to use. 'duckduckgo' is free — "
                    "prefer it by default. 'tavily' costs money but gives "
                    "higher-quality, AI-optimized results — use it only when "
                    "duckduckgo isn't good enough. Defaults to 'duckduckgo' "
                    "if omitted."
                ),
            },
        },
        "required": ["query"],
    },
)
async def web_search(query: str, provider: str = "duckduckgo") -> str:
    if provider == "tavily":
        return await _search_tavily(query)
    if provider == "duckduckgo":
        return await _search_duckduckgo(query)
    raise ValueError(f"Unknown search provider: {provider}")
