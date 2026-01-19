import os
from dotenv import load_dotenv

# Load environment variables from .env file (for local dev)
# Production deployments should use platform environment variables
load_dotenv()

import logging
from fastapi import FastAPI, Depends, HTTPException, Request
import fastapi
import asyncio
import json
import httpx
from fastapi.middleware.cors import CORSMiddleware
from .utils.security import SecurityHeadersMiddleware
from .observability import logger as obs_logger, setup_logging
from .routes.devtools import router as devtools_router
from .routes.document import router as document_router
from .routes.research import router as research_router
from .routes.safety import router as safety_router
from .routes.feature_flags import router as flags_router
from .routes.auth import router as auth_router
from .plugins import sdk as plugin_sdk
from .routes.account import router as account_router
from .routes.assets import router as assets_router
from .routes.agents import router as agents_router
from .routes.tools import router as tools_router
from .routes.intelligence import router as intelligence_router
from .routes.markets import router as markets_router
from .routes.health import router as health_router
from .routes.education import router as education_router
from .routes.business import router as business_router
from .routes.personal import router as personal_router
from .routes.security import router as security_router
from .routes.web import router as web_router
from .routes.admin import router as admin_router
from sqlmodel import SQLModel, create_engine, Session, select
from .auth.firebase import verify_firebase_token, firebase_auth_required
from .ai.service import ai_service
from .search.tavily import tavily_search
from .models import (
    engine,
    init_db,
    Conversation,
    Message,
    Memory,
    Project,
    Task,
    PromptChain,
    AuditLog,
)
from .routes.export import router as export_router
from .utils.rate_limit import require_rate_limit
from .utils.validation import validate_memory_payload, validate_project_payload, validate_task_payload, require_str_field

# MongoDB imports
from .db_mongo import init_db as init_mongo_db, close_db as close_mongo_db, health_check as mongo_health_check
from .models_agent import Agent as MongoAgent
from .routes.agents_mongo import router as agents_mongo_router

LOG_LEVEL = os.getenv("LOG_LEVEL", "info").upper()
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger("backend")

# Vaelis: backend app title (presentation only)
app = FastAPI(title="Vaelis Backend")


@app.exception_handler(fastapi.HTTPException)
async def http_exception_handler(request: Request, exc: fastapi.HTTPException):
    # Return structured JSON for HTTP errors
    detail = exc.detail if isinstance(exc.detail, (str, dict)) else str(exc.detail)
    
    # Handle dict details (already structured)
    if isinstance(detail, dict):
        payload = detail
        if "ok" not in payload:
            payload["ok"] = False
    else:
        # Handle string details
        payload = {"ok": False, "error": "http_error", "status_code": exc.status_code, "message": detail}
    
    # Add specific message for 401 errors if not present
    if exc.status_code == 401 and "message" not in payload:
        payload["message"] = "Authorization required"
    
    return fastapi.responses.JSONResponse(status_code=exc.status_code, content=payload)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    # Generic handler to avoid leaking internals
    logger.exception("Unhandled exception: %s", exc)
    payload = {"ok": False, "error": "internal_server_error", "message": "An internal error occurred"}
    return fastapi.responses.JSONResponse(status_code=500, content=payload)

# include scaffolding routers
app.include_router(auth_router)
app.include_router(devtools_router)
app.include_router(document_router)
app.include_router(research_router)
app.include_router(safety_router)
app.include_router(flags_router)
app.include_router(account_router)
app.include_router(assets_router)
app.include_router(admin_router)

# include feature routers
app.include_router(agents_router)
app.include_router(agents_mongo_router)  # MongoDB-based agents router
app.include_router(tools_router)
app.include_router(intelligence_router)
app.include_router(markets_router)
app.include_router(health_router)
app.include_router(education_router)
app.include_router(business_router)
app.include_router(personal_router)
app.include_router(security_router)
app.include_router(web_router)

# security headers
app.add_middleware(SecurityHeadersMiddleware)

# CORS configuration - read comma-separated list from env
frontend_origins_str = os.getenv("FRONTEND_ORIGINS", "*")
if frontend_origins_str == "*":
    allow_origins = ["*"]
else:
    allow_origins = [origin.strip() for origin in frontend_origins_str.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],  # This allows Authorization header
)


@app.on_event("startup")
async def startup():
    init_db()
    logger.info("SQL DB initialized")
    
    # Initialize MongoDB if MONGODB_URI is available
    mongodb_uri = os.getenv("MONGODB_URI")
    if mongodb_uri:
        try:
            await init_mongo_db(document_models=[MongoAgent])
            logger.info("MongoDB / Beanie initialized")
        except Exception as e:
            logger.exception(f"Failed to initialize MongoDB: {e}")
            # Don't fail startup if MongoDB is unavailable - allow SQL fallback
    else:
        logger.warning("MONGODB_URI not set - MongoDB features disabled")


@app.on_event("shutdown")
async def shutdown():
    """Gracefully close database connections on shutdown."""
    await close_mongo_db()
    logger.info("Shutdown complete")


@app.get("/")
def root():
    """Root endpoint - provides basic API information"""
    return {
        "service": "Vaelis Backend",
        "status": "running",
        "version": "1.0.0",
        "health_check": "/health"
    }


@app.get("/health")
async def health():
    """
    Health check endpoint that verifies database connectivity.
    Returns 200 if healthy, 503 if database is unreachable.
    """
    response = {
        "status": "ok",
        "sql_db": "connected",
        "mongo_db": "not_configured"
    }
    
    # Check MongoDB health if configured
    mongodb_uri = os.getenv("MONGODB_URI")
    if mongodb_uri:
        try:
            mongo_healthy = await mongo_health_check()
            if mongo_healthy:
                response["mongo_db"] = "connected"
            else:
                response["mongo_db"] = "unreachable"
                response["status"] = "degraded"
                logger.error("MongoDB health check failed")
                return fastapi.responses.JSONResponse(
                    status_code=503,
                    content=response
                )
        except Exception as e:
            logger.exception(f"MongoDB health check error: {e}")
            response["mongo_db"] = "error"
            response["status"] = "degraded"
            return fastapi.responses.JSONResponse(
                status_code=503,
                content=response
            )
    
    return response


@app.post("/ai/generate")
async def generate(payload: dict, response: fastapi.Response, user=Depends(firebase_auth_required)):
    # payload: { mode: str, prompt: str, use_search: bool }
    mode = payload.get("mode", "chat")
    prompt = payload.get("prompt")
    if not prompt or not isinstance(prompt, str):
        raise HTTPException(status_code=400, detail={"ok": False, "error": "prompt required and must be a string"})
    if mode not in ("chat", "think", "study", "build"):
        # allow-list modes and normalize unknowns to chat
        mode = "chat"
    # rate limit check
    try:
        require_rate_limit(request=None, uid=user["uid"])  # request not used in simple limiter
        response.headers["X-RateLimit-Checked"] = "1"
    except Exception as e:
        logger.warning(f"Rate limit check issue: {e}")
        pass
    
    # optional search
    sources = None
    if payload.get("use_search"):
        q = payload.get("search_query") or prompt
        try:
            sources = await tavily_search(q)
        except Exception as e:
            logger.exception(f"Tavily search failed for query '{q}': {e}")
            sources = None
    
    # call AI core with error handling
    try:
        logger.debug(f"Calling AI service for generation: {ai_service.url}")
        res = await ai_service.generate(prompt=prompt, mode=mode, sources=sources)
        logger.info("Groq API connection successful (generate)")
        
        # Check if AI service returned an error
        if res.get("status") == "error":
            logger.error(f"AI service error: {res.get('error')} - {res.get('output')}")
            raise HTTPException(
                status_code=502,
                detail={"ok": False, "error": res.get("error", "ai_service_error"), "message": res.get("output")}
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"AI generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={"ok": False, "error": "Internal server error", "message": "Failed to generate AI response"}
        )
    
    # persist conversation metadata; support appending to existing conversation
    conv_id = payload.get("conv_id")
    try:
        with Session(engine) as session:
            if conv_id:
                conv = session.get(Conversation, conv_id)
                if not conv or conv.user_id != user["uid"]:
                    raise HTTPException(status_code=404, detail="conversation not found")
            else:
                conv = Conversation(user_id=user["uid"], title=(prompt[:120]))
                session.add(conv)
                session.commit()
                session.refresh(conv)
            # persist user message
            user_msg = Message(conversation_id=conv.id, role="user", content=prompt)
            session.add(user_msg)
            session.commit()
            # persist assistant message
            assistant_msg = Message(conversation_id=conv.id, role="assistant", content=str(res.get("output")))
            session.add(assistant_msg)
            session.commit()
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to persist conversation: {e}")
    
    out = res.copy() if isinstance(res, dict) else {"output": str(res)}
    try:
        out["conv_id"] = conv.id
    except Exception:
        pass
    return out


@app.post("/ai/stream")
async def stream_generate(request: Request, user=Depends(firebase_auth_required)):
    # Streaming endpoint: proxy model streaming responses to client as simple SSE (text/event-stream)
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    mode = payload.get("mode", "chat")
    prompt = payload.get("prompt")
    if not prompt:
        raise HTTPException(status_code=400, detail="prompt required")

    sources = None
    if payload.get("use_search"):
        q = payload.get("search_query") or prompt
        sources = await tavily_search(q)

    # use configured AI service settings
    ai_url = getattr(ai_service, "url", None)
    ai_key = getattr(ai_service, "key", None)
    if not ai_key:
        raise HTTPException(status_code=500, detail="AI API key not configured")

    headers = {"Authorization": f"Bearer {ai_key}", "Content-Type": "application/json"}
    
    # Include sources in the prompt if available
    full_prompt = prompt
    if sources and isinstance(sources, dict) and sources.get("items"):
        source_text = "\n".join([f"- {s.get('title', 'Source')}: {s.get('url', '')}\n  Snippet: {s.get('snippet', '')}" for s in sources["items"]])
        full_prompt = f"Use the following sources to answer the prompt:\n{prompt}\n\nSources:\n{source_text}"

    body = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": f"You are a helpful assistant. Mode: {mode}"},
            {"role": "user", "content": full_prompt}
        ],
        "temperature": 0.7,
        "stream": True
    }

    logger.debug(f"Starting Groq stream from {ai_url}/chat/completions")

    async def event_generator():
        try:
            # create or fetch conversation and persist the user's message immediately
            with Session(engine) as session:
                conv_id = payload.get("conv_id")
                if conv_id:
                    conv = session.get(Conversation, conv_id)
                    if not conv or conv.user_id != user["uid"]:
                        raise HTTPException(status_code=404, detail="conversation not found")
                else:
                    conv = Conversation(user_id=user["uid"], title=(prompt[:120]))
                    session.add(conv)
                    session.commit()
                    session.refresh(conv)
                user_msg = Message(conversation_id=conv.id, role="user", content=prompt)
                session.add(user_msg)
                session.commit()

            # inform client of conv id
            yield f"data: {json.dumps({'conv_id': conv.id})}\n\n"

            async with httpx.AsyncClient(timeout=None) as client:
                url = f"{ai_url}/chat/completions"
                async with client.stream("POST", url, json=body, headers=headers) as resp:
                    resp.raise_for_status()
                    logger.info("Groq stream connection successful")
                    accum = ""
                    async for line in resp.aiter_lines():
                        if await request.is_disconnected():
                            return
                        if not line or not line.startswith("data: "):
                            continue
                        if line == "data: [DONE]":
                            break
                        try:
                            json_str = line[6:]
                            data = json.loads(json_str)
                            delta = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                            if delta:
                                accum += delta
                                yield f"data: {json.dumps({'delta': delta})}\n\n"
                        except Exception:
                            continue
                    # after stream completes, persist assistant final message
                    try:
                        with Session(engine) as session:
                            msg = Message(conversation_id=conv.id, role="assistant", content=accum)
                            session.add(msg)
                            session.commit()
                    except Exception:
                        logger.exception("failed to persist streamed conversation")
        except httpx.HTTPError as e:
            err = json.dumps({"error": "model_error", "message": str(e)})
            yield f"data: {err}\n\n"
        except Exception as e:
            err = json.dumps({"error": "server_error", "message": str(e)})
            yield f"data: {err}\n\n"
        yield f"data: {json.dumps({'done': True})}\n\n"

    return fastapi.responses.StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/conversations")
def list_conversations(user=Depends(firebase_auth_required)):
    with Session(engine) as session:
        convs = session.exec(select(Conversation).where(Conversation.user_id == user["uid"]))
        return {"conversations": [c.dict() for c in convs.all()]}


# Memories (short-term & long-term)
@app.post("/memories")
def create_memory(body: dict, user=Depends(firebase_auth_required)):
    content = body.get("content")
    if not content:
        raise HTTPException(status_code=400, detail="content required")
    long_term = bool(body.get("long_term", False))
    conv_id = body.get("conversation_id")
    tags = body.get("tags")
    with Session(engine) as session:
        mem = Memory(user_id=user["uid"], conversation_id=conv_id, content=content, long_term=long_term, tags=",".join(tags) if tags else None)
        session.add(mem)
        session.commit()
        session.refresh(mem)
    return {"memory": mem.dict()}


@app.get("/memories")
def list_memories(long_term: bool = False, user=Depends(firebase_auth_required)):
    with Session(engine) as session:
        q = select(Memory).where(Memory.user_id == user["uid"]).where(Memory.long_term == long_term)
        res = session.exec(q).all()
        return {"memories": [r.dict() for r in res]}


@app.get("/memories/{mem_id}")
def get_memory(mem_id: int, user=Depends(firebase_auth_required)):
    with Session(engine) as session:
        mem = session.get(Memory, mem_id)
        if not mem or mem.user_id != user["uid"]:
            raise HTTPException(status_code=404, detail="not found")
        return {"memory": mem.dict()}


@app.put("/memories/{mem_id}")
def update_memory(mem_id: int, body: dict, user=Depends(firebase_auth_required)):
    # validate body
    if not isinstance(body, dict):
        raise HTTPException(status_code=400, detail="body must be JSON object")
    if "content" in body and (not isinstance(body.get("content"), str) or not body.get("content").strip()):
        raise HTTPException(status_code=400, detail="content must be a non-empty string")
    if "tags" in body and body.get("tags") is not None and not isinstance(body.get("tags"), list):
        raise HTTPException(status_code=400, detail="tags must be a list")
    with Session(engine) as session:
        mem = session.get(Memory, mem_id)
        if not mem or mem.user_id != user["uid"]:
            raise HTTPException(status_code=404, detail="not found")
        if "content" in body:
            mem.content = body.get("content").strip()
        if "visible" in body:
            mem.visible = bool(body.get("visible"))
        if "tags" in body:
            tags = body.get("tags")
            mem.tags = ",".join(tags) if isinstance(tags, list) else tags
        mem.updated_at = __import__("datetime").datetime.utcnow()
        session.add(mem)
        session.commit()
        return {"memory": mem.dict()}


@app.delete("/memories/{mem_id}")
def delete_memory(mem_id: int, user=Depends(firebase_auth_required)):
    with Session(engine) as session:
        mem = session.get(Memory, mem_id)
        if not mem or mem.user_id != user["uid"]:
            raise HTTPException(status_code=404, detail="not found")
        session.delete(mem)
        # audit
        audit = AuditLog(user_id=user["uid"], action="forget_memory", target_type="memory", target_id=mem_id, detail=None)
        session.add(audit)
        session.commit()
        return {"ok": True}


# Projects
@app.post("/projects")
def create_project(body: dict, user=Depends(firebase_auth_required)):
    vals = validate_project_payload(body)
    with Session(engine) as session:
        p = Project(user_id=user["uid"], name=vals["name"], description=vals.get("description"))
        session.add(p)
        session.commit()
        session.refresh(p)
        return {"project": p.dict()}


@app.get("/projects")
def list_projects(user=Depends(firebase_auth_required)):
    with Session(engine) as session:
        res = session.exec(select(Project).where(Project.user_id == user["uid"]))
        return {"projects": [r.dict() for r in res.all()]}


# Tasks
@app.post("/tasks")
def create_task(body: dict, user=Depends(firebase_auth_required)):
    vals = validate_task_payload(body)
    with Session(engine) as session:
        t = Task(user_id=user["uid"], project_id=vals.get("project_id"), title=vals["title"], description=vals.get("description"), status=vals.get("status", "todo"))
        session.add(t)
        session.commit()
        session.refresh(t)
        return {"task": t.dict()}


@app.get("/tasks")
def list_tasks(project_id: int = None, user=Depends(firebase_auth_required)):
    with Session(engine) as session:
        q = select(Task).where(Task.user_id == user["uid"])
        if project_id:
            q = q.where(Task.project_id == project_id)
        res = session.exec(q).all()
        return {"tasks": [r.dict() for r in res]}


# Prompt chains (scaffold)
@app.post("/chains")
def create_chain(body: dict, user=Depends(firebase_auth_required)):
    name = body.get("name")
    if not name:
        raise HTTPException(status_code=400, detail="name required")
    definition = body.get("definition")
    with Session(engine) as session:
        c = PromptChain(user_id=user["uid"], name=name, definition=definition)
        session.add(c)
        session.commit()
        session.refresh(c)
        return {"chain": c.dict()}


@app.get("/chains")
def list_chains(user=Depends(firebase_auth_required)):
    with Session(engine) as session:
        res = session.exec(select(PromptChain).where(PromptChain.user_id == user["uid"]))
        return {"chains": [r.dict() for r in res.all()]}


@app.post("/chains/{chain_id}/run")
async def run_chain(chain_id: int, body: dict = {}, user=Depends(firebase_auth_required)):
    # Minimal runner stub: returns queued response; full runner implementation is out of scope for Phase 1
    with Session(engine) as session:
        chain = session.get(PromptChain, chain_id)
        if not chain or chain.user_id != user["uid"]:
            raise HTTPException(status_code=404, detail="not found")
    return {"status": "queued", "chain_id": chain_id}


@app.get("/conversations/{conv_id}")
def get_conversation(conv_id: int, user=Depends(firebase_auth_required)):
    with Session(engine) as session:
        conv = session.get(Conversation, conv_id)
        if not conv or conv.user_id != user["uid"]:
            raise HTTPException(status_code=404, detail="Not found")
        msgs = session.exec(select(Message).where(Message.conversation_id == conv_id)).all()
        return {"conversation": conv.dict(), "messages": [m.dict() for m in msgs]}


app.include_router(export_router)

# simple retry/dedupe cache
_REQ_CACHE = {}
_REQ_TTL = int(os.getenv("REQ_CACHE_TTL", "30"))


@app.post("/conversations/{conv_id}/pin")
def pin_conversation(conv_id: int, body: dict, user=Depends(firebase_auth_required)):
    with Session(engine) as session:
        conv = session.get(Conversation, conv_id)
        if not conv or conv.user_id != user["uid"]:
            raise HTTPException(status_code=404, detail="Not found")
        conv.pinned = bool(body.get("pinned", True))
        session.add(conv)
        session.commit()
        return {"ok": True, "pinned": conv.pinned}


@app.post("/conversations/{conv_id}/tags")
def set_tags(conv_id: int, body: dict, user=Depends(firebase_auth_required)):
    tags = body.get("tags")
    if tags is None:
        raise HTTPException(status_code=400, detail="tags required")
    if not isinstance(tags, list):
        raise HTTPException(status_code=400, detail="tags must be list")
    with Session(engine) as session:
        conv = session.get(Conversation, conv_id)
        if not conv or conv.user_id != user["uid"]:
            raise HTTPException(status_code=404, detail="Not found")
        conv.tags = ",".join(tags)
        session.add(conv)
        session.commit()
        return {"ok": True, "tags": tags}


@app.post("/ai/retry")
async def ai_retry(body: dict, response: fastapi.Response, user=Depends(firebase_auth_required)):
    conv_id = body.get("conv_id")
    message_id = body.get("message_id")
    if not conv_id or not message_id:
        raise HTTPException(status_code=400, detail="conv_id and message_id required")
    with Session(engine) as session:
        msg = session.get(Message, message_id)
        if not msg or msg.conversation_id != conv_id:
            raise HTTPException(status_code=404, detail="message not found")
    # dedupe using hash of content
    import hashlib, time

    key = hashlib.sha256(msg.content.encode()).hexdigest()
    now = int(time.time())
    cached = _REQ_CACHE.get(key)
    if cached and now - cached < _REQ_TTL:
        # inform client via header and HTTP 409
        response.headers["X-RateLimit-Reason"] = "duplicate_retry"
        raise HTTPException(status_code=409, detail="Duplicate retry too soon")
    _REQ_CACHE[key] = now
    # call AI core
    try:
        res = await ai_service.generate(prompt=msg.content, mode="chat")
    except Exception as e:
        logger.exception("ai retry failed")
        raise HTTPException(status_code=502, detail="AI service error")
    # persist
    try:
        with Session(engine) as session:
            new_msg = Message(conversation_id=conv_id, role="assistant", content=str(res.get("output")))
            session.add(new_msg)
            session.commit()
    except Exception:
        logger.exception("failed to persist retry message")
    return {"result": res}


@app.post("/conversations/{conv_id}/generate_title")
async def generate_title(conv_id: int, user=Depends(firebase_auth_required)):
    with Session(engine) as session:
        conv = session.get(Conversation, conv_id)
        if not conv or conv.user_id != user["uid"]:
            raise HTTPException(status_code=404, detail="Not found")
        msgs = session.exec(select(Message).where(Message.conversation_id == conv_id)).all()
        aggregated = "\n".join([m.content for m in msgs][:10])
    prompt = f"Generate a short (under 8 words) meaningful title for this conversation:\n{aggregated}"
    res = await ai_service.generate(prompt=prompt, mode="study")
    title = None
    if isinstance(res.get("output"), str):
        title = res.get("output").strip().split('\n')[0][:120]
    if title:
        with Session(engine) as session:
            conv = session.get(Conversation, conv_id)
            conv.title = title
            session.add(conv)
            session.commit()
    return {"title": title}
