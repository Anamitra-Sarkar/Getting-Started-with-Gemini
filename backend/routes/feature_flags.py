from fastapi import APIRouter

router = APIRouter(prefix="/flags", tags=["flags"])

# simple in-memory feature flags
_FLAGS = {"new_ui": False, "credits": False}


@router.get("/")
def list_flags():
    return _FLAGS


@router.post("/{name}/toggle")
def toggle_flag(name: str):
    if name not in _FLAGS:
        return {"error": "unknown flag"}
    _FLAGS[name] = not _FLAGS[name]
    return {"name": name, "value": _FLAGS[name]}
