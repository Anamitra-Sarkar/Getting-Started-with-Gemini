import os
from typing import Optional, Dict, Any
from fastapi import HTTPException, Request

try:
    import firebase_admin
    from firebase_admin import auth as firebase_auth, credentials
except Exception:  # pragma: no cover - external dependency may be missing in test env
    firebase_admin = None
    firebase_auth = None
    credentials = None

# Initialize firebase admin lazily
_initialized = False
# simple in-memory cache for verified tokens: token -> (decoded, ts)
_TOKEN_CACHE: Dict[str, Dict[str, Any]] = {}
_TOKEN_TTL = int(os.getenv("FIREBASE_TOKEN_CACHE_TTL", "60"))


def init_firebase():
    """Initialize firebase admin SDK if available. Safe to call multiple times."""
    global _initialized
    if _initialized:
        return
    if firebase_admin is None:
        # firebase-admin not available; downstream calls will raise
        _initialized = False
        return
    cred_path = os.getenv("FIREBASE_CREDENTIALS_JSON")
    try:
        if cred_path:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        else:
            firebase_admin.initialize_app()
        _initialized = True
    except Exception:
        # if initialization fails, keep _initialized False and allow verify to raise
        _initialized = False


def verify_firebase_token(id_token: str) -> Dict[str, Any]:
    """Verify ID token using firebase-admin with a short in-memory cache.

    Raises HTTPException(401) on failure without leaking internals.
    """
    init_firebase()
    if firebase_auth is None:
        raise HTTPException(status_code=500, detail="Authentication service not available")

    # cache lookup
    import time

    entry = _TOKEN_CACHE.get(id_token)
    now = int(time.time())
    if entry and now - entry.get("ts", 0) < _TOKEN_TTL:
        return entry.get("decoded")

    try:
        decoded = firebase_auth.verify_id_token(id_token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired authentication token")

    # cache decoded token
    try:
        _TOKEN_CACHE[id_token] = {"decoded": decoded, "ts": now}
    except Exception:
        pass
    return decoded


def firebase_auth_required(request: Request):
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header missing")
    token = auth.split(" ", 1)[1]
    return verify_firebase_token(token)
