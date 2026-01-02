from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
import difflib
from typing import Optional
from pathlib import Path
from ..ai.service import ai_service

router = APIRouter(prefix="/dev", tags=["dev"])


class DiffRequest(BaseModel):
    a: str
    b: str


@router.get("/repo")
def repo_info():
    # lightweight repo awareness stub
    return {"repo": "getting-started-with-vaelis", "status": "ok"}


@router.post("/diff")
def diff(req: DiffRequest):
    a_lines = req.a.splitlines(keepends=True)
    b_lines = req.b.splitlines(keepends=True)
    diff = difflib.unified_diff(a_lines, b_lines, fromfile="a", tofile="b")
    return {"diff": "".join(diff)}


@router.get("/file")
def read_file(path: str = Query(..., description="Relative path under repo to read (safe)")):
    # Prevent path traversal by resolving within repo root
    repo_root = Path.cwd()
    target = (repo_root / Path(path)).resolve()
    try:
        if repo_root not in target.parents and repo_root != target.parent:
            raise HTTPException(status_code=400, detail="invalid path")
        if not target.exists() or not target.is_file():
            raise HTTPException(status_code=404, detail="not found")
        content = target.read_text(encoding="utf-8")
        return {"path": str(target.relative_to(repo_root)), "content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class StackTraceRequest(BaseModel):
    trace: str
    context: Optional[str] = None


@router.post("/stacktrace")
async def explain_stacktrace(req: StackTraceRequest):
    # Use AI service to generate an explanation for the stacktrace; the AIService will sanitize outputs
    prompt = f"Explain the following stacktrace and suggest fixes:\n{req.trace}\n\nContext:\n{req.context or 'none'}"
    res = await ai_service.generate(prompt=prompt, mode="code")
    return {"explanation": res}
