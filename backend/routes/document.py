from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/documents", tags=["documents"])


class DocumentCreate(BaseModel):
    title: str
    template: Optional[str] = None
    content: Optional[str] = None


@router.post("/")
def create_document(d: DocumentCreate):
    # stub: create a document entry and return id
    return {"id": 1, "title": d.title, "status": "created"}


@router.get("/{doc_id}/versions")
def list_versions(doc_id: int):
    return {"doc_id": doc_id, "versions": []}


@router.post("/{doc_id}/export")
def export_document(doc_id: int, fmt: str = "md"):
    # stubbed export
    return {"doc_id": doc_id, "format": fmt, "url": f"/export/{doc_id}.{fmt}"}
