from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import httpx
import re

from ..search.tavily import tavily_search

router = APIRouter(prefix="/research", tags=["research"])


class ResearchSessionCreate(BaseModel):
    query: str
    notes: Optional[str] = None


@router.post("/sessions")
def create_session(r: ResearchSessionCreate):
    # stub: create a research session and return id
    return {"session_id": 1, "query": r.query}


@router.get("/sessions/{sid}")
def get_session(sid: int):
    return {"session_id": sid, "results": []}


class SearchRequest(BaseModel):
    q: str


@router.post("/search")
async def search(req: SearchRequest):
    try:
        res = await tavily_search(req.q)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class CiteRequest(BaseModel):
    url: str


@router.post("/cite")
async def cite(req: CiteRequest):
    url = req.url
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(url)
            r.raise_for_status()
            text = r.text
            # extract title
            m = re.search(r"<title>(.*?)</title>", text, re.IGNORECASE | re.DOTALL)
            title = m.group(1).strip() if m else None
            # extract meta description
            m2 = re.search(r'<meta\s+name="description"\s+content="(.*?)"', text, re.IGNORECASE)
            desc = m2.group(1).strip() if m2 else None
            return {"url": url, "title": title, "description": desc}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
