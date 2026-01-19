import os
import httpx
import logging
import asyncio
from typing import Optional, Dict, Any

from .identity import label_response, sanitize_raw

logger = logging.getLogger("backend.ai.service")

GEMINI_URL = os.getenv("GEMINI_API_URL", "https://api.groq.com/openai/v1")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")


class AIService:
    def __init__(self):
        self.url = GEMINI_URL
        self.key = GEMINI_KEY
        logger.debug(f"AIService initialized with URL: {self.url}")

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
                # Groq uses OpenAI-compatible format
                # Include sources in the prompt if available
                full_prompt = prompt
                if sources and isinstance(sources, dict) and sources.get("items"):
                    source_text = "\n".join([f"- {s.get('title', 'Source')}: {s.get('url', '')}\n  Snippet: {s.get('snippet', '')}" for s in sources["items"]])
                    full_prompt = f"Use the following sources to answer the prompt:\n{prompt}\n\nSources:\n{source_text}"

                body = {
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": f"You are a helpful assistant. Mode: {mode}"},
                        {"role": "user", "content": full_prompt}
                    ],
                    "temperature": 0.7,
                }
                
                logger.debug(f"Calling Groq API at {self.url}/chat/completions (Attempt {attempt + 1})")
                
                async with httpx.AsyncClient(timeout=60.0) as client:
                    r = await client.post(f"{self.url}/chat/completions", json=body, headers=headers)
                    r.raise_for_status()
                    out = r.json()
                    
                    logger.info("Groq API connection successful")
                    
                    # Extract text from Groq response (OpenAI format)
                    choices = out.get("choices", [])
                    if choices:
                        text = choices[0].get("message", {}).get("content", "")
                    else:
                        text = str(out)
                    
                    return label_response(text, sources=sources, raw=out)
                    
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
        logger.error(f"AI service failed after {max_retries + 1} attempts", exc_info=True, extra={"last_error": str(last_error)})
        return {
            "output": "AI service temporarily unavailable. Please try again later.",
            "error": "service_error",
            "status": "error"
        }


ai_service = AIService()
