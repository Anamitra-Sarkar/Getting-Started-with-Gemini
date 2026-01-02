"""
Identity and response sanitization utilities for Vaelis.
This module centralizes the assistant display name and strips provider/internal metadata
from model responses before they are returned to clients or persisted.
"""
from typing import Any, Dict

ASSISTANT_NAME = "Vaelis"


def sanitize_raw(raw: Any) -> Any:
    """Remove common provider/internal keys from raw model response dicts.
    Non-destructive and conservative: if input is not a dict, return as-is.
    """
    if not isinstance(raw, dict):
        return raw
    forbidden = {"model", "provider", "internal", "system_prompt", "api_version"}
    safe: Dict[str, Any] = {}
    for k, v in raw.items():
        if k in forbidden:
            continue
        # strip nested provider info conservatively
        if isinstance(v, dict):
            safe[k] = {kk: vv for kk, vv in v.items() if kk not in forbidden}
        else:
            safe[k] = v
    return safe


def label_response(output_text: str, sources: Any = None, raw: Any = None) -> Dict[str, Any]:
    """Return a sanitized, labeled response object that the rest of the app expects.

    The returned shape is intentionally simple and stable:
      { assistant: "Vaelis", output: str, sources: [...], raw: <sanitized> }
    """
    return {
        "assistant": ASSISTANT_NAME,
        "output": output_text,
        "sources": sources or [],
        "raw": sanitize_raw(raw),
    }
