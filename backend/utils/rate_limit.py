import time
from typing import Dict
from fastapi import HTTPException, Request

# simple in-memory token-bucket rate limiter per user
_BUCKETS: Dict[str, Dict] = {}

RATE_LIMIT = int(__import__("os").environ.get("RATE_LIMIT_PER_MIN", "60"))
BURST = int(__import__("os").environ.get("RATE_LIMIT_BURST", "20"))

def allow_request(uid: str) -> bool:
    now = time.time()
    bucket = _BUCKETS.get(uid)
    if not bucket:
        _BUCKETS[uid] = {"tokens": RATE_LIMIT, "last": now}
        return True
    # refill
    elapsed = now - bucket["last"]
    refill = elapsed * (RATE_LIMIT / 60.0)
    bucket["tokens"] = min(BURST, bucket["tokens"] + refill)
    bucket["last"] = now
    if bucket["tokens"] >= 1:
        bucket["tokens"] -= 1
        return True
    return False

def require_rate_limit(request: Request, uid: str):
    if not allow_request(uid):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
