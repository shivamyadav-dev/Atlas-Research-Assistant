from typing import List, Dict
import os
import requests
from langchain.tools import tool  # type: ignore

GOOGLE_SEARCH_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

@tool
def google_search(query: str, num_results: int = 5) -> List[Dict[str, str]]:
    """Search the web using Google Custom Search. Returns a list of results with title, link, and snippet.
    Note: Requires GOOGLE_SEARCH_API_KEY and GOOGLE_CSE_ID. Returns empty list if not configured."""
    if not GOOGLE_SEARCH_API_KEY or not GOOGLE_CSE_ID:
        return []
    try:
        params = {
            "key": GOOGLE_SEARCH_API_KEY,
            "cx": GOOGLE_CSE_ID,
            "q": query,
            "num": max(1, min(num_results, 10)),
        }
        resp = requests.get("https://www.googleapis.com/customsearch/v1", params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        items = data.get("items", [])
        results: List[Dict[str, str]] = []
        for it in items:
            results.append({
                "title": it.get("title", ""),
                "link": it.get("link", ""),
                "snippet": it.get("snippet", ""),
            })
        return results
    except Exception as e:
        # Return empty list on any error to allow LLM-only mode to continue
        return []

@tool
def fetch_url(url: str) -> str:
    """Fetch raw HTML/text content from a URL."""
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    # Return up to 20k chars to avoid overly large payloads
    return r.text[:20000]
