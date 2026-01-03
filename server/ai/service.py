import os
import httpx
from typing import List, Dict, Any, Optional
import asyncio

GEMINI_API_URL = os.getenv("GEMINI_API_URL", "https://api.generativeai.example/v1")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TAVILY_API_URL = os.getenv("TAVILY_API_URL", "https://api.tavily.com/search")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

class AIService:
    def __init__(self):
        self.gemini_url = GEMINI_API_URL
        self.gemini_key = GEMINI_API_KEY
        self.tavily_url = TAVILY_API_URL
        self.tavily_key = TAVILY_API_KEY

    async def tavily_search(self, query: str) -> List[Dict[str, Any]]:
        if not self.tavily_key:
            raise RuntimeError("TAVILY_API_KEY not configured")
        headers = {"Authorization": f"Bearer {self.tavily_key}"}
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(self.tavily_url, params={"q": query}, headers=headers)
            r.raise_for_status()
            return r.json()

    async def call_gemini(self, prompt: str, mode: str = "chat", context: Optional[List[Dict]]=None) -> Dict[str, Any]:
        if not self.gemini_key:
            raise RuntimeError("GEMINI_API_KEY not configured")
        headers = {"Authorization": f"Bearer {self.gemini_key}", "Content-Type": "application/json"}
        body = {
            "model": "gemini-2.0-flash",
            "mode": mode,
            "prompt": prompt,
            "context": context or []
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post(f"{self.gemini_url}/generate", json=body, headers=headers)
            r.raise_for_status()
            return r.json()

    async def chat_with_search(self, query: str, mode: str = "chat") -> Dict[str, Any]:
        # Get fresh sources from Tavily, then provide to Gemini as structured context
        results = await self.tavily_search(query)
        context = [{"source": r.get("url"), "title": r.get("title"), "snippet": r.get("snippet")} for r in results.get("items", [])][:5]
        prompt = f"Use the following sources to answer concisely and cite sources:\n{query}\nSources:\n" + "\n".join([f"- {c['title']}: {c['source']}" for c in context])
        res = await self.call_gemini(prompt, mode=mode, context=context)
        # Ensure Gemini outputs include citations (do not fabricate)
        return {"ai": res, "sources": context}

    async def analyze_image(self, image_bytes: bytes, instruction: str = "Describe and extract details") -> Dict[str, Any]:
        # Send image as multipart to Gemini vision endpoint if supported
        if not self.gemini_key:
            raise RuntimeError("GEMINI_API_KEY not configured")
        headers = {"Authorization": f"Bearer {self.gemini_key}"}
        files = {"image": ("upload.jpg", image_bytes, "image/jpeg")}
        data = {"instruction": instruction, "model": "gemini-2.0-flash"}
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post(f"{self.gemini_url}/vision:analyze", headers=headers, data=data, files=files)
            r.raise_for_status()
            return r.json()

ai_service = AIService()
