"""MongoDB-based agents router using Beanie for async persistence."""
import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from beanie import PydanticObjectId

from ..models_agent import Agent
from ..auth.firebase import firebase_auth_required

logger = logging.getLogger("backend.routes.agents_mongo")
router = APIRouter(prefix="/agents-mongo", tags=["agents-mongo"])


class AgentCreate(BaseModel):
    name: str
    description: Optional[str] = None
    config: Optional[dict] = None
    memory_scope: str = "conversation"
    public: bool = False


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[dict] = None
    memory_scope: Optional[str] = None
    status: Optional[str] = None
    public: Optional[bool] = None


@router.get("/stats")
async def get_stats(user=Depends(firebase_auth_required)):
    """Get dashboard statistics for the current user."""
    try:
        # Count agents owned by user
        agents_count = await Agent.find(Agent.owner_id == user["uid"]).count()
        
        # For now, use static values for runs and tools as they may not be in MongoDB yet
        runs = 0
        tools = 20
        
        # Calculate intelligence score based on activity
        intelligence_score = min(100, 50 + (agents_count * 5))
        
        return {
            "agents": agents_count,
            "runs": runs,
            "tools": tools,
            "intelligence_score": intelligence_score
        }
    except Exception as e:
        logger.exception(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail={"ok": False, "error": "Failed to retrieve statistics"})


@router.post("/")
async def create_agent(body: AgentCreate, user=Depends(firebase_auth_required)):
    """Create a new agent."""
    try:
        agent = Agent(
            name=body.name,
            description=body.description,
            owner_id=user["uid"],
            config=body.config,
            memory_scope=body.memory_scope,
            public=body.public,
            status="idle"
        )
        await agent.insert()
        
        return {"agent": agent.model_dump()}
    except Exception as e:
        logger.exception(f"Failed to create agent: {e}")
        raise HTTPException(status_code=500, detail={"ok": False, "error": "Failed to create agent"})


@router.get("/")
async def list_agents(user=Depends(firebase_auth_required)):
    """List all agents for the current user."""
    try:
        agents = await Agent.find(Agent.owner_id == user["uid"]).to_list()
        return {"agents": [agent.model_dump() for agent in agents]}
    except Exception as e:
        logger.exception(f"Failed to list agents: {e}")
        raise HTTPException(status_code=500, detail={"ok": False, "error": "Failed to list agents"})


@router.get("/{agent_id}")
async def get_agent(agent_id: str, user=Depends(firebase_auth_required)):
    """Get a specific agent by ID."""
    try:
        # Validate ObjectId format
        try:
            obj_id = PydanticObjectId(agent_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid agent ID format")
        
        agent = await Agent.get(obj_id)
        if not agent or agent.owner_id != user["uid"]:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return {"agent": agent.model_dump()}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to get agent: {e}")
        raise HTTPException(status_code=500, detail={"ok": False, "error": "Failed to retrieve agent"})


@router.put("/{agent_id}")
async def update_agent(agent_id: str, body: AgentUpdate, user=Depends(firebase_auth_required)):
    """Update an agent."""
    try:
        # Validate ObjectId format
        try:
            obj_id = PydanticObjectId(agent_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid agent ID format")
        
        agent = await Agent.get(obj_id)
        if not agent or agent.owner_id != user["uid"]:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Update fields if provided
        if body.name is not None:
            agent.name = body.name
        if body.description is not None:
            agent.description = body.description
        if body.config is not None:
            agent.config = body.config
        if body.memory_scope is not None:
            agent.memory_scope = body.memory_scope
        if body.status is not None:
            if body.status not in ["idle", "running", "paused", "stopped", "error"]:
                raise HTTPException(status_code=400, detail="Invalid status")
            agent.status = body.status
        if body.public is not None:
            agent.public = body.public
        
        agent.updated_at = datetime.utcnow()
        await agent.save()
        
        return {"agent": agent.model_dump()}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to update agent: {e}")
        raise HTTPException(status_code=500, detail={"ok": False, "error": "Failed to update agent"})


@router.delete("/{agent_id}")
async def delete_agent(agent_id: str, user=Depends(firebase_auth_required)):
    """Delete an agent."""
    try:
        # Validate ObjectId format
        try:
            obj_id = PydanticObjectId(agent_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid agent ID format")
        
        agent = await Agent.get(obj_id)
        if not agent or agent.owner_id != user["uid"]:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        await agent.delete()
        return {"ok": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to delete agent: {e}")
        raise HTTPException(status_code=500, detail={"ok": False, "error": "Failed to delete agent"})


@router.patch("/{agent_id}")
async def patch_agent(agent_id: str, body: AgentUpdate, user=Depends(firebase_auth_required)):
    """Partially update an agent (PATCH method)."""
    # PATCH is identical to PUT for this implementation
    return await update_agent(agent_id, body, user)
