from __future__ import annotations

import asyncio
import time
from typing import Any, Dict
from urllib.parse import urlparse
import httpx

class RateLimiter:
    """Per-domain rate limiter ensuring >= 2s interval between requests to the same domain.
    
    Shared across sources sharing the same domain (e.g. goethe.de, kochimuzirisbiennale.org).
    """
    def __init__(self, default_delay: float = 2.0):
        self.default_delay = default_delay
        self.last_request_time: Dict[str, float] = {}
        self.locks: Dict[str, asyncio.Lock] = {}

    def _get_lock(self, domain: str) -> asyncio.Lock:
        if domain not in self.locks:
            self.locks[domain] = asyncio.Lock()
        return self.locks[domain]

    async def wait_for_domain(self, domain: str, delay: float | None = None):
        delay = delay or self.default_delay
        lock = self._get_lock(domain)
        async with lock:
            now = time.time()
            last = self.last_request_time.get(domain, 0.0)
            elapsed = now - last
            if elapsed < delay:
                await asyncio.sleep(delay - elapsed)
            self.last_request_time[domain] = time.time()

rate_limiter = RateLimiter(default_delay=2.0)

async def async_fetch_url(
    client: httpx.AsyncClient,
    url: str,
    etag: str | None = None,
    last_modified: str | None = None,
    domain_delay: float = 2.0
) -> Dict[str, Any]:
    """Async polite fetch with per-domain throttling, headers, and conditional GET."""
    domain = urlparse(url).netloc.lower()
    await rate_limiter.wait_for_domain(domain, delay=domain_delay)

    headers = {
        "User-Agent": "AOIA-FineArts-Bot/1.0 (+https://github.com/aoia; contact@aoia.art)",
        "Accept": "text/html,application/xhtml+xml,application/pdf,application/xml;q=0.9,*/*;q=0.8"
    }
    if etag:
        headers["If-None-Match"] = etag
    if last_modified:
        headers["If-Modified-Since"] = last_modified

    try:
        resp = await client.get(url, headers=headers, follow_redirects=True, timeout=12.0)
        return {
            "status_code": resp.status_code,
            "text": resp.text if resp.status_code == 200 else "",
            "content": resp.content if resp.status_code == 200 else b"",
            "headers": dict(resp.headers),
            "etag": resp.headers.get("etag"),
            "last_modified": resp.headers.get("last-modified"),
            "url": str(resp.url),
            "error": None
        }
    except Exception as e:
        return {
            "status_code": 0,
            "text": "",
            "content": b"",
            "headers": {},
            "etag": None,
            "last_modified": None,
            "url": url,
            "error": str(e)
        }

def fetch_content(url: str) -> str:
    """Synchronous fallback helper."""
    try:
        r = httpx.get(
            url,
            headers={"User-Agent": "AOIA-FineArts-Bot/1.0 (+https://github.com/aoia)"},
            timeout=10.0,
            follow_redirects=True
        )
        return r.text if r.status_code == 200 else ""
    except Exception:
        return ""
