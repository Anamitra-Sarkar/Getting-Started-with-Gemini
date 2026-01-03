from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from ..models import engine, Agent, AgentRun, AgentMemory
from ..auth.firebase import firebase_auth_required
import json

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("/stats")
def get_stats(user=Depends(firebase_auth_required)):
    """Get dashboard statistics for the current user"""
    with Session(engine) as session:
        # Count agents
        agents_count = session.exec(
            select(Agent).where(Agent.user_id == user["uid"])
        ).all()
        agents = len(agents_count)
        
        # Count runs
        runs_count = session.exec(
            select(AgentRun).where(AgentRun.user_id == user["uid"])
        ).all()
        runs = len(runs_count)
        
        # Get tool count from tools router (20 is default)
        tools = 20
        
        # Calculate intelligence score based on activity
        intelligence_score = min(100, 50 + (agents * 5) + (runs * 2))
        
        return {
            "agents": agents,
            "runs": runs,
            "tools": tools,
            "intelligence_score": intelligence_score
        }


class AgentCreate(BaseModel):
    name: str
    description: Optional[str] = None
    config: Optional[dict] = None
    memory_scope: str = "conversation"


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[dict] = None
    memory_scope: Optional[str] = None
    status: Optional[str] = None


class AgentRunRequest(BaseModel):
    input_data: dict


@router.post("/")
def create_agent(body: AgentCreate, user=Depends(firebase_auth_required)):
    """Create a new agent"""
    with Session(engine) as session:
        agent = Agent(
            user_id=user["uid"],
            name=body.name,
            description=body.description,
            config=json.dumps(body.config) if body.config else None,
            memory_scope=body.memory_scope,
            status="idle"
        )
        session.add(agent)
        session.commit()
        session.refresh(agent)
        return {"agent": agent.dict()}


@router.get("/")
def list_agents(user=Depends(firebase_auth_required)):
    """List all agents for the current user"""
    with Session(engine) as session:
        agents = session.exec(
            select(Agent).where(Agent.user_id == user["uid"])
        ).all()
        return {"agents": [a.dict() for a in agents]}


@router.get("/{agent_id}")
def get_agent(agent_id: int, user=Depends(firebase_auth_required)):
    """Get a specific agent"""
    with Session(engine) as session:
        agent = session.get(Agent, agent_id)
        if not agent or agent.user_id != user["uid"]:
            raise HTTPException(status_code=404, detail="Agent not found")
        return {"agent": agent.dict()}


@router.put("/{agent_id}")
def update_agent(agent_id: int, body: AgentUpdate, user=Depends(firebase_auth_required)):
    """Update an agent"""
    with Session(engine) as session:
        agent = session.get(Agent, agent_id)
        if not agent or agent.user_id != user["uid"]:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        if body.name is not None:
            agent.name = body.name
        if body.description is not None:
            agent.description = body.description
        if body.config is not None:
            agent.config = json.dumps(body.config)
        if body.memory_scope is not None:
            agent.memory_scope = body.memory_scope
        if body.status is not None:
            if body.status not in ["idle", "running", "paused", "stopped", "error"]:
                raise HTTPException(status_code=400, detail="Invalid status")
            agent.status = body.status
        
        agent.updated_at = datetime.utcnow()
        session.add(agent)
        session.commit()
        session.refresh(agent)
        return {"agent": agent.dict()}


@router.delete("/{agent_id}")
def delete_agent(agent_id: int, user=Depends(firebase_auth_required)):
    """Delete an agent"""
    with Session(engine) as session:
        agent = session.get(Agent, agent_id)
        if not agent or agent.user_id != user["uid"]:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        session.delete(agent)
        session.commit()
        return {"ok": True}


@router.post("/{agent_id}/run")
def run_agent(agent_id: int, body: AgentRunRequest, user=Depends(firebase_auth_required)):
    """Start an agent run"""
    with Session(engine) as session:
        agent = session.get(Agent, agent_id)
        if not agent or agent.user_id != user["uid"]:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Create a run record
        run = AgentRun(
            agent_id=agent_id,
            user_id=user["uid"],
            status="running",
            input_data=json.dumps(body.input_data)
        )
        session.add(run)
        
        # Update agent status
        agent.status = "running"
        agent.updated_at = datetime.utcnow()
        session.add(agent)
        
        session.commit()
        session.refresh(run)
        
        return {"run": run.dict(), "message": "Agent run started"}


@router.post("/{agent_id}/pause")
def pause_agent(agent_id: int, user=Depends(firebase_auth_required)):
    """Pause a running agent"""
    with Session(engine) as session:
        agent = session.get(Agent, agent_id)
        if not agent or agent.user_id != user["uid"]:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        if agent.status != "running":
            raise HTTPException(status_code=400, detail="Agent is not running")
        
        agent.status = "paused"
        agent.updated_at = datetime.utcnow()
        session.add(agent)
        session.commit()
        
        return {"ok": True, "status": "paused"}


@router.post("/{agent_id}/stop")
def stop_agent(agent_id: int, user=Depends(firebase_auth_required)):
    """Stop a running agent"""
    with Session(engine) as session:
        agent = session.get(Agent, agent_id)
        if not agent or agent.user_id != user["uid"]:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        agent.status = "stopped"
        agent.updated_at = datetime.utcnow()
        session.add(agent)
        session.commit()
        
        return {"ok": True, "status": "stopped"}


@router.get("/{agent_id}/runs")
def list_runs(agent_id: int, user=Depends(firebase_auth_required)):
    """List all runs for an agent"""
    with Session(engine) as session:
        agent = session.get(Agent, agent_id)
        if not agent or agent.user_id != user["uid"]:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        runs = session.exec(
            select(AgentRun).where(AgentRun.agent_id == agent_id)
        ).all()
        return {"runs": [r.dict() for r in runs]}


@router.get("/{agent_id}/memory")
def get_agent_memory(agent_id: int, user=Depends(firebase_auth_required)):
    """Get agent memory"""
    with Session(engine) as session:
        agent = session.get(Agent, agent_id)
        if not agent or agent.user_id != user["uid"]:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        memories = session.exec(
            select(AgentMemory).where(AgentMemory.agent_id == agent_id)
        ).all()
        return {"memories": [m.dict() for m in memories]}


@router.post("/{agent_id}/memory")
def set_agent_memory(
    agent_id: int,
    body: dict,
    user=Depends(firebase_auth_required)
):
    """Set agent memory"""
    with Session(engine) as session:
        agent = session.get(Agent, agent_id)
        if not agent or agent.user_id != user["uid"]:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        key = body.get("key")
        value = body.get("value")
        scope = body.get("scope", agent.memory_scope)
        scope_id = body.get("scope_id")
        
        if not key or not value:
            raise HTTPException(status_code=400, detail="key and value required")
        
        memory = AgentMemory(
            agent_id=agent_id,
            scope=scope,
            scope_id=scope_id,
            key=key,
            value=json.dumps(value) if isinstance(value, (dict, list)) else str(value)
        )
        session.add(memory)
        session.commit()
        session.refresh(memory)
        
        return {"memory": memory.dict()}
