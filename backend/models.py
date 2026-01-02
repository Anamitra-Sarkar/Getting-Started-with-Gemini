from sqlmodel import SQLModel, Field, create_engine
from typing import Optional
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./backend_data.db")
engine = create_engine(DATABASE_URL, echo=False)


class Conversation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str
    title: Optional[str] = None
    pinned: bool = False
    tags: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int
    role: str
    content: str
    meta: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Memory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str
    conversation_id: Optional[int] = None
    content: str
    long_term: bool = False
    tags: Optional[str] = None
    visible: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str
    name: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str
    project_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    status: str = "todo"
    priority: Optional[int] = None
    due_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PromptChain(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str
    name: str
    definition: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AuditLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[str]
    action: str
    target_type: Optional[str]
    target_id: Optional[int]
    detail: Optional[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Organization(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Account(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str
    org_id: Optional[int] = None
    credits: float = 0.0
    role: str = "member"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CreditTransaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    account_id: int
    amount: float
    reason: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


def init_db():
    SQLModel.metadata.create_all(engine)
