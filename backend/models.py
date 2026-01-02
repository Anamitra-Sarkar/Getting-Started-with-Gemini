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


# Agent system models
class Agent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str
    name: str
    description: Optional[str] = None
    config: Optional[str] = None  # JSON config
    status: str = "idle"  # idle, running, paused, stopped, error
    memory_scope: str = "conversation"  # conversation, project, global
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AgentRun(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    agent_id: int
    user_id: str
    status: str = "running"  # running, completed, failed, paused
    input_data: Optional[str] = None
    output_data: Optional[str] = None
    error: Optional[str] = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


class AgentMemory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    agent_id: int
    scope: str  # conversation, project, global
    scope_id: Optional[int] = None
    key: str
    value: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Tool system models
class Tool(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    category: str  # web, finance, health, education, business, etc.
    description: Optional[str] = None
    config: Optional[str] = None
    enabled: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ToolPermission(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str
    tool_id: int
    granted: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ToolUsage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str
    tool_id: int
    conversation_id: Optional[int] = None
    status: str = "success"  # success, failed, dry_run
    input_data: Optional[str] = None
    output_data: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Intelligence analysis models
class IntentAnalysis(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int
    message_id: int
    detected_intent: str
    confidence: float
    ambiguity_score: float
    suggestions: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class BiasDetection(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content_type: str  # message, source, news
    content_id: int
    bias_type: str  # confirmation, anchoring, availability, etc.
    confidence: float
    explanation: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CredibilityScore(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    url: str
    domain: str
    score: float  # 0-1
    factors: Optional[str] = None  # JSON of scoring factors
    last_checked: datetime = Field(default_factory=datetime.utcnow)


# Research and analysis models
class ResearchSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str
    query: str
    notes: Optional[str] = None
    status: str = "active"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Citation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int
    url: str
    title: Optional[str] = None
    summary: Optional[str] = None
    credibility_score: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Market and finance models
class MarketAnalysis(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str
    symbol: str
    analysis_type: str  # earnings, sector, macro, risk
    data: str  # JSON analysis data
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PortfolioRisk(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str
    portfolio_data: str  # JSON
    risk_score: float
    recommendations: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Health and wellness models
class HealthAnalysis(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str
    analysis_type: str  # wellness, longevity, nutrition, fitness
    input_data: str
    recommendations: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Education and career models
class LearningGap(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str
    subject: str
    current_level: str
    target_level: str
    gaps: str  # JSON array of gaps
    recommendations: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CareerAnalysis(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str
    analysis_type: str  # resume, salary, path, skills
    input_data: str
    result: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Business and strategy models
class BusinessAnalysis(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str
    analysis_type: str  # market_sizing, moat, pricing, gtm, swot
    input_data: str
    result: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Meta-cognition models
class DecisionAnalysis(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str
    decision_context: str
    blind_spots: Optional[str] = None
    second_order_effects: Optional[str] = None
    cognitive_biases: Optional[str] = None
    recommendation: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Personal OS models
class LifeConstraint(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str
    constraint_type: str
    description: str
    priority: int
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Goal(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str
    title: str
    description: Optional[str] = None
    category: str  # personal, career, health, financial, etc.
    status: str = "active"
    deadline: Optional[datetime] = None
    progress: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ConsequenceModel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str
    decision: str
    short_term: str  # JSON
    long_term: str  # JSON
    regret_probability: float
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Security and trust models
class TrustScore(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str
    user_id: str
    score: float  # 0-1
    factors: str  # JSON
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SecurityIncident(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    incident_type: str  # prompt_injection, unauthorized_access, etc.
    user_id: Optional[str] = None
    severity: str  # low, medium, high, critical
    description: str
    resolved: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)


def init_db():
    SQLModel.metadata.create_all(engine)
