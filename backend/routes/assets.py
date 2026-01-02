import os
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlmodel import Session
from ..models import engine, AuditLog
from ..auth.firebase import firebase_auth_required
import aiofiles

router = APIRouter(prefix="/assets", tags=["assets"])

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./backend_uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_asset(file: UploadFile = File(...), user=Depends(firebase_auth_required)):
    filename = file.filename
    dest = os.path.join(UPLOAD_DIR, filename)
    try:
        async with aiofiles.open(dest, 'wb') as f:
            content = await file.read()
            await f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    # audit
    with Session(engine) as session:
        session.add(AuditLog(user_id=user["uid"], action="upload_asset", target_type="asset", detail=filename))
        session.commit()
    return {"filename": filename, "path": dest}


@router.get("/")
def list_assets(user=Depends(firebase_auth_required)):
    items = []
    for fn in os.listdir(UPLOAD_DIR):
        p = os.path.join(UPLOAD_DIR, fn)
        if os.path.isfile(p):
            items.append({"filename": fn, "path": p})
    return {"assets": items}
