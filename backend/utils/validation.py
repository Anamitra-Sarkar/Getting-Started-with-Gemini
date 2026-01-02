from fastapi import HTTPException
from typing import Any, Dict, List, Optional


def require_str_field(body: Dict[str, Any], key: str, max_len: Optional[int] = None) -> str:
    v = body.get(key)
    if v is None or not isinstance(v, str) or not v.strip():
        raise HTTPException(status_code=400, detail=f"{key} required and must be non-empty string")
    v = v.strip()
    if max_len and len(v) > max_len:
        raise HTTPException(status_code=400, detail=f"{key} too long (max {max_len})")
    return v


def validate_memory_payload(body: Dict[str, Any]) -> Dict[str, Any]:
    content = body.get("content")
    if content is None or not isinstance(content, str) or not content.strip():
        raise HTTPException(status_code=400, detail="content required and must be non-empty string")
    long_term = bool(body.get("long_term", False))
    conv = body.get("conversation_id")
    if conv is not None:
        try:
            conv = int(conv)
        except Exception:
            raise HTTPException(status_code=400, detail="conversation_id must be integer")
    tags = body.get("tags")
    if tags is not None and not isinstance(tags, list):
        raise HTTPException(status_code=400, detail="tags must be a list of strings")
    return {"content": content.strip(), "long_term": long_term, "conversation_id": conv, "tags": tags}


def validate_project_payload(body: Dict[str, Any]) -> Dict[str, Any]:
    name = body.get("name")
    if name is None or not isinstance(name, str) or not name.strip():
        raise HTTPException(status_code=400, detail="name required and must be non-empty string")
    description = body.get("description")
    if description is not None and not isinstance(description, str):
        raise HTTPException(status_code=400, detail="description must be string")
    return {"name": name.strip(), "description": description}


def validate_task_payload(body: Dict[str, Any]) -> Dict[str, Any]:
    title = body.get("title")
    if title is None or not isinstance(title, str) or not title.strip():
        raise HTTPException(status_code=400, detail="title required and must be non-empty string")
    project_id = body.get("project_id")
    if project_id is not None:
        try:
            project_id = int(project_id)
        except Exception:
            raise HTTPException(status_code=400, detail="project_id must be integer")
    status = body.get("status", "todo")
    return {"title": title.strip(), "project_id": project_id, "status": status, "description": body.get("description")}
