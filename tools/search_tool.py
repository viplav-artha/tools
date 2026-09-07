import os

import httpx
from dotenv import load_dotenv

from tools.registry import tool

load_dotenv()

TAVILY_SEARCH_URL = "https://api.tavily.com/search"


@tool(
    name="web_search",
    description=(
        "Search the web for current information on a topic. Returns a short "
        "list of relevant results with titles, URLs, and content snippets."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query to look up on the web.",
            }
        },
        "required": ["query"],
    },
)
async def web_search(query: str) -> str:
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
