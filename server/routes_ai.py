from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from .auth import get_current_user
from .ai.service import ai_service
from sqlmodel import Session, select
from .db import engine
from .models import Conversation, Message
from typing import List

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/chat")
async def chat(query: dict, user=Depends(get_current_user)):
    mode = query.get("mode", "chat")
    text = query.get("text")
    if not text:
        raise HTTPException(status_code=400, detail="No text provided")
    res = await ai_service.call_gemini(text, mode=mode)
    # persist conversation
    with Session(engine) as session:
        conv = Conversation(user_id=user.id, title=(text[:80]))
        session.add(conv)
        session.commit()
        session.refresh(conv)
        msg = Message(conversation_id=conv.id, role="assistant", content=str(res))
        session.add(msg)
        session.commit()
    return {"result": res}


@router.post("/search")
async def search(body: dict, user=Depends(get_current_user)):
    q = body.get("q")
    if not q:
        raise HTTPException(status_code=400, detail="Query required")
    res = await ai_service.chat_with_search(q, mode=body.get("mode", "chat"))
    return res


@router.post("/vision")
async def vision(file: UploadFile = File(...), instruction: str = "Describe image", user=Depends(get_current_user)):
    content = await file.read()
    res = await ai_service.analyze_image(content, instruction=instruction)
    return res


@router.get("/conversations")
def list_conversations(user=Depends(get_current_user)):
    with Session(engine) as session:
        convs = session.exec(select(Conversation).where(Conversation.user_id == user.id)).all()
        return {"conversations": [c.dict() for c in convs]}
