"""Beanie Document models for MongoDB persistence."""
from beanie import Document, Indexed
from pydantic import Field
from typing import Optional
from datetime import datetime


class Agent(Document):
    """Agent Document model for MongoDB using Beanie."""
    
    name: str = Field(..., description="Agent name")
    description: Optional[str] = Field(None, description="Agent description")
    owner_id: Indexed(str) = Field(..., description="User ID of the agent owner")
    config: Optional[dict] = Field(None, description="Agent configuration as dict")
    status: str = Field(default="idle", description="Agent status: idle, running, paused, stopped, error")
    memory_scope: str = Field(default="conversation", description="Memory scope: conversation, project, global")
    public: bool = Field(default=False, description="Whether the agent is publicly accessible")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "agents"  # Collection name
        indexes = [
            "owner_id",  # Single field index on owner_id
            [("owner_id", 1), ("name", 1)],  # Compound index on owner + name
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Research Assistant",
                "description": "An agent that helps with research tasks",
                "owner_id": "user123",
                "config": {"model": "gemini-pro", "temperature": 0.7},
                "status": "idle",
                "memory_scope": "conversation",
                "public": False
            }
        }
