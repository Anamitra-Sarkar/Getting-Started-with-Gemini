from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from ..models import engine, Tool, ToolPermission, ToolUsage
from ..auth.firebase import firebase_auth_required
import json

router = APIRouter(prefix="/tools", tags=["tools"])


class ToolCreate(BaseModel):
    name: str
    category: str
    description: Optional[str] = None
    config: Optional[dict] = None


class ToolExecuteRequest(BaseModel):
    input_data: dict
    dry_run: bool = False


@router.get("/")
def list_tools(category: Optional[str] = None, user=Depends(firebase_auth_required)):
    """List all available tools"""
    with Session(engine) as session:
        query = select(Tool).where(Tool.enabled == True)
        if category:
            query = query.where(Tool.category == category)
        
        tools = session.exec(query).all()
        
        # Check permissions for each tool
        tool_list = []
        for tool in tools:
            perm = session.exec(
                select(ToolPermission)
                .where(ToolPermission.user_id == user["uid"])
                .where(ToolPermission.tool_id == tool.id)
            ).first()
            
            tool_dict = tool.dict()
            tool_dict["has_permission"] = perm.granted if perm else False
            tool_list.append(tool_dict)
        
        return {"tools": tool_list}


@router.get("/categories")
def list_categories():
    """List all tool categories"""
    categories = [
        {"name": "web", "description": "Web search and research tools"},
        {"name": "finance", "description": "Financial analysis and market tools"},
        {"name": "crypto", "description": "Cryptocurrency and DeFi tools"},
        {"name": "health", "description": "Health and wellness tools"},
        {"name": "education", "description": "Learning and education tools"},
        {"name": "career", "description": "Career development tools"},
        {"name": "business", "description": "Business strategy and analysis tools"},
        {"name": "creativity", "description": "Creative and media generation tools"},
        {"name": "productivity", "description": "Productivity and automation tools"},
        {"name": "security", "description": "Security and trust tools"},
    ]
    return {"categories": categories}


@router.get("/{tool_id}")
def get_tool(tool_id: int, user=Depends(firebase_auth_required)):
    """Get tool details"""
    with Session(engine) as session:
        tool = session.get(Tool, tool_id)
        if not tool:
            raise HTTPException(status_code=404, detail="Tool not found")
        
        # Check permission
        perm = session.exec(
            select(ToolPermission)
            .where(ToolPermission.user_id == user["uid"])
            .where(ToolPermission.tool_id == tool_id)
        ).first()
        
        tool_dict = tool.dict()
        tool_dict["has_permission"] = perm.granted if perm else False
        
        return {"tool": tool_dict}


@router.post("/{tool_id}/execute")
async def execute_tool(
    tool_id: int,
    body: ToolExecuteRequest,
    user=Depends(firebase_auth_required)
):
    """Execute a tool"""
    with Session(engine) as session:
        tool = session.get(Tool, tool_id)
        if not tool or not tool.enabled:
            raise HTTPException(status_code=404, detail="Tool not found or disabled")
        
        # Check permission
        perm = session.exec(
            select(ToolPermission)
            .where(ToolPermission.user_id == user["uid"])
            .where(ToolPermission.tool_id == tool_id)
        ).first()
        
        if not perm or not perm.granted:
            raise HTTPException(status_code=403, detail="Permission denied for this tool")
        
        # Log the usage
        usage = ToolUsage(
            user_id=user["uid"],
            tool_id=tool_id,
            status="dry_run" if body.dry_run else "success",
            input_data=json.dumps(body.input_data)
        )
        
        try:
            # Tool execution logic would go here
            # For now, return a simulated response
            if body.dry_run:
                output = {
                    "dry_run": True,
                    "would_execute": tool.name,
                    "input": body.input_data
                }
            else:
                output = {
                    "tool": tool.name,
                    "category": tool.category,
                    "result": "Tool execution placeholder",
                    "input": body.input_data
                }
            
            usage.output_data = json.dumps(output)
            session.add(usage)
            session.commit()
            
            return {"output": output, "usage_id": usage.id}
            
        except Exception as e:
            usage.status = "failed"
            usage.error = str(e)
            session.add(usage)
            session.commit()
            raise HTTPException(status_code=500, detail=f"Tool execution failed: {str(e)}")


@router.post("/{tool_id}/permissions")
def grant_permission(tool_id: int, user=Depends(firebase_auth_required)):
    """Grant permission to use a tool"""
    with Session(engine) as session:
        tool = session.get(Tool, tool_id)
        if not tool:
            raise HTTPException(status_code=404, detail="Tool not found")
        
        # Check if permission already exists
        perm = session.exec(
            select(ToolPermission)
            .where(ToolPermission.user_id == user["uid"])
            .where(ToolPermission.tool_id == tool_id)
        ).first()
        
        if perm:
            perm.granted = True
            session.add(perm)
        else:
            perm = ToolPermission(
                user_id=user["uid"],
                tool_id=tool_id,
                granted=True
            )
            session.add(perm)
        
        session.commit()
        return {"ok": True, "granted": True}


@router.delete("/{tool_id}/permissions")
def revoke_permission(tool_id: int, user=Depends(firebase_auth_required)):
    """Revoke permission to use a tool"""
    with Session(engine) as session:
        perm = session.exec(
            select(ToolPermission)
            .where(ToolPermission.user_id == user["uid"])
            .where(ToolPermission.tool_id == tool_id)
        ).first()
        
        if perm:
            perm.granted = False
            session.add(perm)
            session.commit()
        
        return {"ok": True, "granted": False}


@router.get("/{tool_id}/usage")
def get_tool_usage(tool_id: int, user=Depends(firebase_auth_required)):
    """Get usage history for a tool"""
    with Session(engine) as session:
        usages = session.exec(
            select(ToolUsage)
            .where(ToolUsage.user_id == user["uid"])
            .where(ToolUsage.tool_id == tool_id)
        ).all()
        
        return {"usages": [u.dict() for u in usages]}


@router.get("/usage/all")
def get_all_usage(user=Depends(firebase_auth_required)):
    """Get all tool usage for the current user"""
    with Session(engine) as session:
        usages = session.exec(
            select(ToolUsage).where(ToolUsage.user_id == user["uid"])
        ).all()
        
        return {"usages": [u.dict() for u in usages]}


@router.get("/health/status")
def tool_health():
    """Get health status of all tools"""
    with Session(engine) as session:
        tools = session.exec(select(Tool)).all()
        
        health_status = []
        for tool in tools:
            # Simulate health check
            status = {
                "tool_id": tool.id,
                "name": tool.name,
                "category": tool.category,
                "enabled": tool.enabled,
                "status": "healthy" if tool.enabled else "disabled",
                "last_check": datetime.utcnow().isoformat()
            }
            health_status.append(status)
        
        return {"health": health_status}
