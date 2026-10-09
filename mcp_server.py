import json
import os
import httpx
from dotenv import load_dotenv
from fastmcp import FastMCP

from utils import clean_html_to_txt

load_dotenv()

mcp = FastMCP("docs")

SERPER_URL = "https://google.serper.dev/search"


async def search_web(query: str) -> dict | None:
    payload = json.dumps({
        "q": query,
        "num": 2,
    })

    headers = {
        "X-API-KEY": os.getenv("SERPER_API_KEY"),
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            SERPER_URL,
            headers=headers,
            data=payload,
            timeout=30.0,
        )

        response.raise_for_status()
        return response.json()


async def fetch_url(url: str):
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(url, timeout=30.0)
        response.raise_for_status()

        cleaned = clean_html_to_txt(response.text)

        if cleaned: 
            return cleaned

        return response.text


docs_urls = {
    "langchain": "python. llamaindex.ai/en/stable",
    "openai": "platform.openai.com/docs",
    "uv": "docs.astral.sh/uv",
}


@mcp.tool()
async def get_docs(query: str, library: str):
    """
    Search the latest docs for a given query and library.

    Args:
        query: Search query.
        library: langchain, openai, llama-index or uv.

    Returns:
        Documentation text with source links.
    """

    if library not in docs_urls:
        raise ValueError(f"Library '{library}' is not supported.")

    search_query = f"site:{docs_urls[library]} {query}"

    results = await search_web(search_query)

    if not results.get("organic"):
        return "No documentation found."

    text_parts = []

    for result in results["organic"]:
        link = result.get("link")

        if not link:
            continue

        print(f"Fetching: {link}")

        try:
            text = await fetch_url(link)

            if text:
                text_parts.append(
                    f"SOURCE: {link}\n\n{text}"
                )

        except Exception as e:
            print(f"Error fetching {link}: {e}")

    if not text_parts:
        return "No documentation could be extracted."

    return "\n\n".join(text_parts)


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()