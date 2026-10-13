import os
import httpx
from typing import List

def brave_search(query: str) -> List[str]:
    api_key = os.environ.get("BRAVE_API_KEY")
    if not api_key:
        return []
    try:
        headers = {"Accept": "application/json", "Accept-Encoding": "gzip", "X-Subscription-Token": api_key}
        response = httpx.get("https://api.search.brave.com/res/v1/web/search", headers=headers, params={"q": query})
        if response.status_code == 200:
            data = response.json()
            return [result["url"] for result in data.get("web", {}).get("results", [])]
    except Exception as e:
        print(f"Brave Search Error: {e}")
    return []

def run_discovery() -> List[str]:
    queries = ["artist residency open call 2026 deadline", "visual artist grant India applications open"]
    urls = []
    for q in queries:
        urls.extend(brave_search(q))
    return list(set(urls))
