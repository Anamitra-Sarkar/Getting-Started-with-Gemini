import os
import httpx
import logging
import asyncio
from typing import Optional, Dict, Any

from .identity import label_response, sanitize_raw

logger = logging.getLogger("backend.ai.service")

GEMINI_URL = os.getenv("GEMINI_API_URL", "https://api.generativeai.example/v1")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")


class AIService:
    def __init__(self):
        self.url = GEMINI_URL
        self.key = GEMINI_KEY

    async def generate(self, prompt: str, mode: str = "chat", sources: Optional[Dict] = None, max_retries: int = 2) -> Dict[str, Any]:
        # Conservative check; keep env var name for compatibility but avoid exposing provider name in messages
        if not self.key:
            logger.error("AI API key not configured")
            return {
                "output": "AI service is currently unavailable. Please configure the GEMINI_API_KEY environment variable.",
                "error": "service_unavailable",
                "status": "error"
            }
        
        # Retry logic with exponential backoff
        retry_delay = 1  # Start with 1 second delay
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
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
                    
            except httpx.TimeoutException as e:
                last_error = e
                logger.warning(f"AI service timeout on attempt {attempt + 1}/{max_retries + 1}: {e}")
                if attempt < max_retries:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
                    
            except httpx.HTTPStatusError as e:
                last_error = e
                # Don't retry on 4xx errors (client errors)
                if 400 <= e.response.status_code < 500:
                    logger.error(f"AI service client error: {e}")
                    return {
                        "output": "Invalid request to AI service.",
                        "error": "client_error",
                        "status": "error",
                        "status_code": e.response.status_code
                    }
                # Retry on 5xx errors (server errors)
                logger.warning(f"AI service error on attempt {attempt + 1}/{max_retries + 1}: {e}")
                if attempt < max_retries:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                    
            except httpx.HTTPError as e:
                last_error = e
                logger.warning(f"AI service HTTP error on attempt {attempt + 1}/{max_retries + 1}: {e}")
                if attempt < max_retries:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                    
            except Exception as e:
                last_error = e
                logger.exception(f"Unexpected AI service error: {e}")
                return {
                    "output": "An unexpected error occurred while processing your request.",
                    "error": "unknown_error",
                    "status": "error"
                }
        
        # All retries exhausted
        logger.exception(f"AI service failed after {max_retries + 1} attempts: {last_error}")
        return {
            "output": "AI service temporarily unavailable. Please try again later.",
            "error": "service_error",
            "status": "error"
        }


ai_service = AIService()
