import os
import httpx
from typing import Optional, Dict, Any

from .identity import label_response, sanitize_raw

GEMINI_URL = os.getenv("GEMINI_API_URL", "https://api.generativeai.example/v1")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")


class AIService:
    def __init__(self):
        self.url = GEMINI_URL
        self.key = GEMINI_KEY

    async def generate(self, prompt: str, mode: str = "chat", sources: Optional[Dict] = None) -> Dict[str, Any]:
        # Conservative check; keep env var name for compatibility but avoid exposing provider name in messages
        if not self.key:
            raise RuntimeError("AI API key not configured")
        headers = {"Authorization": f"Bearer {self.key}", "Content-Type": "application/json"}
        body = {
            "model": "gemini-2.0-flash",
            "mode": mode,
            "prompt": prompt,
            "sources": sources or [],
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post(f"{self.url}/generate", json=body, headers=headers)
            r.raise_for_status()
            out = r.json()
            # Normalize the returned structure and remove provider/internal metadata before returning
            text = out.get("text") if isinstance(out, dict) else out
            return label_response(text or str(out), sources=sources, raw=out)


ai_service = AIService()
