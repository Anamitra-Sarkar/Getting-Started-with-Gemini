# backend/ai/identity.py
from typing import Optional, Dict, Any


def label_response(text: str, sources: Optional[Dict] = None, raw: Optional[Any] = None) -> Dict[str, Any]:
    """Label and normalize AI response with metadata."""
    return {
        "output": text,
        "sources": sources or [],
        "raw": raw
    }


def sanitize_raw(text: str) -> str:
    """Sanitize raw response text."""
    return text