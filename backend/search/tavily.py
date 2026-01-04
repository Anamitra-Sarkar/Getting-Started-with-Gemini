import os
import httpx
from typing import List, Dict
import time
from urllib.parse import urlparse

# simple in-memory cache: query -> (timestamp, result)
_CACHE: Dict[str, Dict] = {}
_CACHE_TTL = int(os.getenv("TAVILY_CACHE_TTL", "300"))

TAVILY_URL = os.getenv("TAVILY_API_URL", "https://api.tavily.com/search")
TAVILY_KEY = os.getenv("TAVILY_API_KEY")


async def tavily_search(query: str) -> Dict:
    if not TAVILY_KEY:
        return {"items": [], "error": "Search service not configured"}
    
    try:
        # simple cache
        now = int(time.time())
        cached = _CACHE.get(query)
        if cached and now - cached.get("ts", 0) < _CACHE_TTL:
            return cached.get("data")
        headers = {"Authorization": f"Bearer {TAVILY_KEY}"}
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(TAVILY_URL, params={"q": query, "size": 5}, headers=headers)
            r.raise_for_status()
            data = r.json()
            # normalize to items list with title, url, snippet, timestamp
            items = []
            seen = set()
            for it in data.get("items", [])[:10]:
                url = it.get("url")
                if not url:
                    continue
                # dedupe by netloc+path
                p = urlparse(url)
                key = f"{p.netloc}{p.path}"
                if key in seen:
                    continue
                seen.add(key)
                items.append({
                    "title": it.get("title"),
                    "url": url,
                    "snippet": it.get("snippet"),
                    "timestamp": it.get("timestamp")
                })
                if len(items) >= 5:
                    break
            out = {"items": items}
            _CACHE[query] = {"ts": now, "data": out}
            return out
    except Exception as e:
        # Return empty results on error to allow the app to continue functioning
        return {"items": [], "error": str(e)}
