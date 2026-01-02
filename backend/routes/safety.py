from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/safety", tags=["safety"])


class SafetyMode(BaseModel):
    enabled: bool


_SAFETY_ENABLED = True


@router.get("/mode")
def get_mode():
    return {"enabled": _SAFETY_ENABLED}


@router.post("/mode")
def set_mode(m: SafetyMode):
    global _SAFETY_ENABLED
    _SAFETY_ENABLED = bool(m.enabled)
    return {"enabled": _SAFETY_ENABLED}
