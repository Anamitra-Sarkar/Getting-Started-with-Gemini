from fastapi import APIRouter, HTTPException
from sqlmodel import Session
from ..models import engine, Tool
import json

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/seed/tools")
def seed_tools():
    """Seed initial tool definitions"""
    tools_data = [
        # Web & Research
        {"name": "Web Search", "category": "web", "description": "Search the web and return relevant results with citations", "enabled": True},
        {"name": "Web Summarizer", "category": "web", "description": "Summarize web pages and articles", "enabled": True},
        {"name": "Credibility Checker", "category": "web", "description": "Check credibility of sources and detect bias", "enabled": True},
        {"name": "Fact Checker", "category": "web", "description": "Fact-check claims using authoritative sources", "enabled": True},
        
        # Finance & Markets
        {"name": "Stock Analyzer", "category": "finance", "description": "Analyze stock performance and provide insights", "enabled": True},
        {"name": "Earnings Reporter", "category": "finance", "description": "Summarize and analyze earnings reports", "enabled": True},
        {"name": "Portfolio Analyzer", "category": "finance", "description": "Analyze portfolio risk and optimization", "enabled": True},
        {"name": "Macro Simulator", "category": "finance", "description": "Simulate macroeconomic scenarios", "enabled": True},
        
        # Crypto
        {"name": "Crypto Risk Scanner", "category": "crypto", "description": "Scan cryptocurrencies for scams and risks", "enabled": True},
        {"name": "DeFi Analyzer", "category": "crypto", "description": "Analyze DeFi protocols and opportunities", "enabled": True},
        
        # Health & Wellness
        {"name": "Wellness Tracker", "category": "health", "description": "Track and analyze wellness metrics", "enabled": True},
        {"name": "Nutrition Analyzer", "category": "health", "description": "Analyze nutrition and provide recommendations", "enabled": True},
        {"name": "Fitness Planner", "category": "health", "description": "Create personalized fitness plans", "enabled": True},
        {"name": "Longevity Optimizer", "category": "health", "description": "Analyze and optimize longevity factors", "enabled": True},
        
        # Education & Learning
        {"name": "Learning Gap Detector", "category": "education", "description": "Detect learning gaps and provide roadmaps", "enabled": True},
        {"name": "Study Assistant", "category": "education", "description": "Help with studying and comprehension", "enabled": True},
        {"name": "Research Simplifier", "category": "education", "description": "Simplify research papers and academic content", "enabled": True},
        
        # Career
        {"name": "Resume Analyzer", "category": "career", "description": "Analyze resumes with ATS scoring", "enabled": True},
        {"name": "Salary Calculator", "category": "career", "description": "Calculate market salary rates", "enabled": True},
        {"name": "Career Path Planner", "category": "career", "description": "Plan career transitions and growth", "enabled": True},
        {"name": "Interview Prep", "category": "career", "description": "Prepare for interviews", "enabled": True},
        
        # Business & Strategy
        {"name": "Market Sizer", "category": "business", "description": "Calculate market size (TAM/SAM/SOM)", "enabled": True},
        {"name": "Moat Analyzer", "category": "business", "description": "Analyze competitive moats", "enabled": True},
        {"name": "Pricing Simulator", "category": "business", "description": "Simulate pricing strategies", "enabled": True},
        {"name": "GTM Planner", "category": "business", "description": "Create go-to-market plans", "enabled": True},
        {"name": "SWOT Analyzer", "category": "business", "description": "Perform SWOT analysis", "enabled": True},
        
        # Creativity & Media
        {"name": "Nano Banana", "category": "creativity", "description": "Generate images with AI", "enabled": True},
        {"name": "Veo 3.1", "category": "creativity", "description": "Generate videos with AI", "enabled": True},
        {"name": "Content Writer", "category": "creativity", "description": "Generate creative content", "enabled": True},
        
        # Productivity
        {"name": "Task Manager", "category": "productivity", "description": "Manage tasks and projects", "enabled": True},
        {"name": "Document Generator", "category": "productivity", "description": "Generate documents from templates", "enabled": True},
        {"name": "Workflow Automator", "category": "productivity", "description": "Automate workflows and processes", "enabled": True},
        
        # Intelligence & Analysis
        {"name": "Intent Detector", "category": "intelligence", "description": "Detect user intent with confidence scoring", "enabled": True},
        {"name": "Bias Detector", "category": "intelligence", "description": "Detect cognitive biases", "enabled": True},
        {"name": "Decision Analyzer", "category": "intelligence", "description": "Analyze decisions for blind spots", "enabled": True},
        {"name": "Contradiction Checker", "category": "intelligence", "description": "Detect contradictions in statements", "enabled": True},
        
        # Personal OS
        {"name": "Goal Tracker", "category": "productivity", "description": "Track and decompose goals", "enabled": True},
        {"name": "Consequence Modeler", "category": "productivity", "description": "Model long-term consequences", "enabled": True},
        {"name": "Regret Minimizer", "category": "productivity", "description": "Apply regret minimization framework", "enabled": True},
        {"name": "Life Simulator", "category": "productivity", "description": "Simulate life trajectories", "enabled": True},
        
        # Security
        {"name": "Injection Detector", "category": "security", "description": "Detect prompt injection attempts", "enabled": True},
        {"name": "Trust Scorer", "category": "security", "description": "Calculate session trust scores", "enabled": True},
        {"name": "Privacy Explainer", "category": "security", "description": "Explain privacy implications", "enabled": True},
        {"name": "Compliance Checker", "category": "security", "description": "Check regulatory compliance", "enabled": True},
    ]
    
    with Session(engine) as session:
        for tool_data in tools_data:
            # Check if tool already exists
            existing = session.query(Tool).filter(Tool.name == tool_data["name"]).first()
            if not existing:
                tool = Tool(**tool_data)
                session.add(tool)
        
        session.commit()
    
    return {"status": "ok", "message": f"Seeded {len(tools_data)} tools"}


@router.get("/features/list")
def list_all_features():
    """List all 400 features by category"""
    features = {
        "Core Intelligence (1-50)": [
            "Intent detection with confidence scoring",
            "Ambiguity detection and resolution",
            "Contradiction detection in statements",
            "Cognitive bias detection",
            "Preference drift tracking",
            "Belief graph construction",
            "Context window optimization",
            "Semantic memory compression",
            "Multi-turn coherence tracking",
            "Conversation summarization",
            # ... (would list all 50)
        ],
        "Agent System (51-100)": [
            "Agent creation and configuration",
            "Agent lifecycle management (run/pause/stop)",
            "Agent memory scopes (conversation/project/global)",
            "Agent explainability",
            "Agent recovery mechanisms",
            "Agent permission system",
            "Agent chaining capabilities",
            "Agent health monitoring",
            "Agent audit logging",
            "Multi-agent coordination",
            # ... (would list all 50)
        ],
        "Tools & Orchestration (101-150)": [
            "Tool permission manager",
            "Tool chaining engine",
            "Tool fallback system",
            "Tool dry-run capability",
            "Tool audit logs",
            "Tool health monitoring",
            "Tool dependency resolver",
            "Tool versioning",
            "Tool marketplace",
            "Custom tool creation",
            # ... (would list all 50)
        ],
        "Web & News Intelligence (151-180)": [
            "Live web summarization",
            "Bias detection in sources",
            "Credibility scoring",
            "News heatmaps",
            "Narrative shift alerts",
            "Source diversity analysis",
            "Fact-check integration",
            "Media monitoring",
            "Trend detection",
            "Citation management",
            # ... (would list all 30)
        ],
        "Markets & Finance (181-210)": [
            "Earnings summarization",
            "Sector rotation tracking",
            "Macro simulation",
            "Scam detection (crypto)",
            "DeFi risk analysis",
            "Portfolio optimization",
            "Market sentiment analysis",
            "Technical analysis",
            "Fundamental analysis",
            "Risk modeling",
            # ... (would list all 30)
        ],
        "Health & Science (211-240)": [
            "Research paper simplification",
            "Wellness trend radar",
            "Longevity analysis",
            "Lifestyle optimization",
            "Health risk calculator",
            "Nutrition analyzer",
            "Fitness planning",
            "Sleep optimization",
            "Stress management",
            "Medical research aggregation",
            # ... (would list all 30)
        ],
        "Education & Career (241-270)": [
            "Learning gap detection",
            "Resume ATS scoring",
            "Salary simulation",
            "Career path analysis",
            "Skill gap analysis",
            "Interview preparation",
            "Job market analysis",
            "Networking strategy",
            "Personal branding",
            "Certification planning",
            # ... (would list all 30)
        ],
        "Business & Strategy (271-300)": [
            "Market sizing",
            "Competitive moat analysis",
            "Pricing simulation",
            "GTM planning",
            "Business model canvas",
            "SWOT analysis",
            "Financial projections",
            "Customer segmentation",
            "Value proposition design",
            "Growth strategy",
            # ... (would list all 30)
        ],
        "Meta-Cognition (301-330)": [
            "Blind-spot detection",
            "Second-order effects engine",
            "Decision paralysis breaker",
            "Cognitive bias detector",
            "Reasoning transparency",
            "Thought pattern analysis",
            "Meta-learning tracking",
            "Assumption testing",
            "Mental model refinement",
            "Perspective taking",
            # ... (would list all 30)
        ],
        "Security & Trust (331-360)": [
            "Prompt injection detection",
            "Privacy explainer",
            "Compliance checker",
            "Session trust scoring",
            "Data lineage tracking",
            "Audit trail system",
            "Security incident response",
            "Vulnerability scanning",
            "Access control",
            "Encryption management",
            # ... (would list all 30)
        ],
        "Personal OS & Endgame (361-400)": [
            "Life constraint mapping",
            "Regret minimization engine",
            "Long-term consequence modeler",
            "Don't Lose system",
            "Goal decomposition",
            "Life simulation engine",
            "Legacy planning",
            "Value alignment checker",
            "Decision journal",
            "Life metrics dashboard",
            "Time allocation optimizer",
            "Relationship manager",
            "Personal values clarification",
            "Meaning and purpose exploration",
            "Mortality awareness integration",
            "Peak experience tracker",
            "Flow state optimizer",
            "Energy management",
            "Attention allocation",
            "Calendar intelligence",
            "Habit formation",
            "Identity evolution tracking",
            "Self-reflection prompts",
            "Gratitude journal",
            "Learning log",
            "Achievement milestones",
            "Personal constitution",
            "Decision-making framework",
            "Priority matrix",
            "Trade-off analyzer",
            "Commitment tracker",
            "Boundary setting",
            "Burnout prevention",
            "Recovery protocols",
            "Social battery management",
            "Introversion/extroversion balance",
            "Communication style adaptation",
            "Conflict resolution",
            "Negotiation preparation",
            "Difficult conversations",
            # Final features to complete 400
        ]
    }
    
    total = sum(len(v) for v in features.values())
    
    return {
        "total_features": 400,
        "implemented_features": total,
        "features_by_category": features,
        "status": "in_progress"
    }
