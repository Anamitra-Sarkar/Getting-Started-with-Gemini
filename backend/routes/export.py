from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from ..auth.firebase import firebase_auth_required
from ..models import engine
from sqlmodel import Session, select
from ..models import Conversation, Message
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import datetime
from ..observability import logger

router = APIRouter(prefix="/export", tags=["export"])


@router.get("/markdown/{conv_id}")
def export_markdown(conv_id: int, user=Depends(firebase_auth_required)):
    with Session(engine) as session:
        conv = session.get(Conversation, conv_id)
        if not conv or conv.user_id != user["uid"]:
            raise HTTPException(status_code=404, detail="Not found")
        msgs = session.exec(select(Message).where(Message.conversation_id == conv_id)).all()
        try:
            md = f"# {conv.title or 'Conversation'}\n\n"
            for m in msgs:
                role = m.role
                md += f"**{role}**: {m.content}\n\n"
            headers = {"Content-Disposition": f"attachment; filename=conversation-{conv_id}.md"}
            return StreamingResponse(BytesIO(md.encode()), media_type="text/markdown", headers=headers)
        except Exception as e:
            logger.exception("export_markdown failed")
            return JSONResponse(status_code=500, content={"error": "export_failed", "message": "Failed to export markdown"})


@router.get("/pdf/{conv_id}")
def export_pdf(conv_id: int, user=Depends(firebase_auth_required)):
    with Session(engine) as session:
        conv = session.get(Conversation, conv_id)
        if not conv or conv.user_id != user["uid"]:
            raise HTTPException(status_code=404, detail="Not found")
        msgs = session.exec(select(Message).where(Message.conversation_id == conv_id)).all()
        buf = BytesIO()
        p = canvas.Canvas(buf, pagesize=letter)
        width, height = letter
        y = height - 72
        p.setFont("Helvetica-Bold", 14)
        p.drawString(72, y, conv.title or "Conversation")
        y -= 28
        p.setFont("Helvetica", 10)
        for m in msgs:
            lines = m.content.split('\n')
            for ln in lines:
                if y < 72:
                    p.showPage()
                    y = height - 72
                p.drawString(72, y, f"[{m.role}] {ln}")
                y -= 14
            y -= 6
        p.showPage()
        p.save()
        buf.seek(0)
        try:
            filename = f"conversation-{conv_id}-{datetime.datetime.utcnow().isoformat()}.pdf"
            return StreamingResponse(buf, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=\"{filename}\""})
        except Exception:
            logger.exception("export_pdf failed")
            return JSONResponse(status_code=500, content={"error": "export_failed", "message": "Failed to export pdf"})


@router.post("/messages")
def export_selected_messages(body: dict, user=Depends(firebase_auth_required)):
    ids = body.get("message_ids")
    if not ids or not isinstance(ids, list):
        raise HTTPException(status_code=400, detail="message_ids required")
    with Session(engine) as session:
        try:
            msgs = session.exec(select(Message).where(Message.id.in_(ids))).all()
            md = "# Selected Messages\n\n"
            for m in msgs:
                md += f"**{m.role}**: {m.content}\n\n"
            headers = {"Content-Disposition": f"attachment; filename=selected-messages.md"}
            return StreamingResponse(BytesIO(md.encode()), media_type="text/markdown", headers=headers)
        except Exception:
            logger.exception("export_selected_messages failed")
            return JSONResponse(status_code=500, content={"error": "export_failed", "message": "Failed to export messages"})
