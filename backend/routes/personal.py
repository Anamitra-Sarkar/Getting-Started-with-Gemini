from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from ..models import engine, LifeConstraint, Goal, ConsequenceModel
from ..auth.firebase import firebase_auth_required
from ..ai.service import ai_service
import json

router = APIRouter(prefix="/personal", tags=["personal"])


class ConstraintCreate(BaseModel):
    constraint_type: str  # time, money, health, family, location, etc.
    description: str
    priority: int = 5  # 1-10


class GoalCreate(BaseModel):
    title: str
    description: Optional[str] = None
    category: str
    deadline: Optional[str] = None


class ConsequenceRequest(BaseModel):
    decision: str
    context: Optional[str] = None
    timeframes: List[str] = ["1 month", "1 year", "5 years", "10 years"]


class RegretMinimizationRequest(BaseModel):
    decision: str
    options: List[str]
    values: Optional[List[str]] = None


@router.post("/constraints")
def create_constraint(body: ConstraintCreate, user=Depends(firebase_auth_required)):
    """Map life constraints"""
    with Session(engine) as session:
        constraint = LifeConstraint(
            user_id=user["uid"],
            constraint_type=body.constraint_type,
            description=body.description,
            priority=body.priority
        )
        session.add(constraint)
        session.commit()
        session.refresh(constraint)
        
        return {"constraint": constraint.dict()}


@router.get("/constraints")
def list_constraints(user=Depends(firebase_auth_required)):
    """List all life constraints"""
    with Session(engine) as session:
        constraints = session.exec(
            select(LifeConstraint).where(LifeConstraint.user_id == user["uid"])
        ).all()
        
        return {"constraints": [c.dict() for c in constraints]}


@router.put("/constraints/{constraint_id}")
def update_constraint(
    constraint_id: int,
    body: dict,
    user=Depends(firebase_auth_required)
):
    """Update a constraint"""
    with Session(engine) as session:
        constraint = session.get(LifeConstraint, constraint_id)
        if not constraint or constraint.user_id != user["uid"]:
            raise HTTPException(status_code=404, detail="Constraint not found")
        
        if "description" in body:
            constraint.description = body["description"]
        if "priority" in body:
            constraint.priority = int(body["priority"])
        
        session.add(constraint)
        session.commit()
        session.refresh(constraint)
        
        return {"constraint": constraint.dict()}


@router.delete("/constraints/{constraint_id}")
def delete_constraint(constraint_id: int, user=Depends(firebase_auth_required)):
    """Delete a constraint"""
    with Session(engine) as session:
        constraint = session.get(LifeConstraint, constraint_id)
        if not constraint or constraint.user_id != user["uid"]:
            raise HTTPException(status_code=404, detail="Constraint not found")
        
        session.delete(constraint)
        session.commit()
        
        return {"ok": True}


@router.post("/goals")
def create_goal(body: GoalCreate, user=Depends(firebase_auth_required)):
    """Create a life goal"""
    with Session(engine) as session:
        deadline = None
        if body.deadline:
            try:
                deadline = datetime.fromisoformat(body.deadline)
            except:
                pass
        
        goal = Goal(
            user_id=user["uid"],
            title=body.title,
            description=body.description,
            category=body.category,
            deadline=deadline,
            status="active"
        )
        session.add(goal)
        session.commit()
        session.refresh(goal)
        
        return {"goal": goal.dict()}


@router.get("/goals")
def list_goals(
    category: Optional[str] = None,
    status: Optional[str] = None,
    user=Depends(firebase_auth_required)
):
    """List goals"""
    with Session(engine) as session:
        query = select(Goal).where(Goal.user_id == user["uid"])
        
        if category:
            query = query.where(Goal.category == category)
        if status:
            query = query.where(Goal.status == status)
        
        goals = session.exec(query).all()
        
        return {"goals": [g.dict() for g in goals]}


@router.put("/goals/{goal_id}")
def update_goal(goal_id: int, body: dict, user=Depends(firebase_auth_required)):
    """Update a goal"""
    with Session(engine) as session:
        goal = session.get(Goal, goal_id)
        if not goal or goal.user_id != user["uid"]:
            raise HTTPException(status_code=404, detail="Goal not found")
        
        if "title" in body:
            goal.title = body["title"]
        if "description" in body:
            goal.description = body["description"]
        if "status" in body:
            goal.status = body["status"]
        if "progress" in body:
            goal.progress = float(body["progress"])
        
        session.add(goal)
        session.commit()
        session.refresh(goal)
        
        return {"goal": goal.dict()}


@router.post("/goals/{goal_id}/decompose")
async def decompose_goal(goal_id: int, user=Depends(firebase_auth_required)):
    """Decompose a goal into actionable steps"""
    with Session(engine) as session:
        goal = session.get(Goal, goal_id)
        if not goal or goal.user_id != user["uid"]:
            raise HTTPException(status_code=404, detail="Goal not found")
        
        try:
            prompt = f"""Decompose this goal into actionable steps:

Goal: {goal.title}
Description: {goal.description or 'Not provided'}
Category: {goal.category}
Deadline: {goal.deadline.isoformat() if goal.deadline else 'Not set'}

Provide:
1. Major milestones (3-5)
2. Detailed action steps for each milestone
3. Dependencies between steps
4. Estimated time for each step
5. Resources needed
6. Potential obstacles
7. Success metrics

Respond in JSON format."""
            
            result = await ai_service.generate(prompt=prompt, mode="study")
            
            return {"decomposition": result.get("output")}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Goal decomposition failed: {str(e)}")


@router.post("/consequences/model")
async def model_consequences(body: ConsequenceRequest, user=Depends(firebase_auth_required)):
    """Model long-term consequences of a decision"""
    try:
        prompt = f"""Model consequences of this decision:

Decision: {body.decision}
Context: {body.context or 'Not provided'}

Analyze consequences at these timeframes: {', '.join(body.timeframes)}

For each timeframe, provide:
1. Likely outcomes (best case, base case, worst case)
2. Secondary effects (ripple effects)
3. Reversibility (can this be undone?)
4. Compounding effects
5. Opportunity costs

Also analyze:
- Regret probability (0-1)
- Irreversible consequences
- Path dependencies created

Respond in JSON format."""
        
        result = await ai_service.generate(prompt=prompt, mode="think")
        
        try:
            analysis = json.loads(result.get("output", "{}"))
            regret_prob = float(analysis.get("regret_probability", 0.5))
        except:
            analysis = {}
            regret_prob = 0.5
        
        # Store consequence model
        with Session(engine) as session:
            consequence = ConsequenceModel(
                user_id=user["uid"],
                decision=body.decision,
                short_term=json.dumps(analysis.get("short_term", {})),
                long_term=json.dumps(analysis.get("long_term", {})),
                regret_probability=regret_prob
            )
            session.add(consequence)
            session.commit()
            session.refresh(consequence)
        
        return {"model": result.get("output"), "model_id": consequence.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Consequence modeling failed: {str(e)}")


@router.post("/regret/minimize")
async def minimize_regret(body: RegretMinimizationRequest, user=Depends(firebase_auth_required)):
    """Apply regret minimization framework"""
    try:
        prompt = f"""Apply regret minimization framework:

Decision: {body.decision}
Options: {json.dumps(body.options)}
Personal Values: {json.dumps(body.values) if body.values else 'Not specified'}

Use Jeff Bezos "Regret Minimization Framework":
1. Project yourself to age 80
2. For each option, assess: "Will I regret not doing this?"
3. Consider which regrets you can live with
4. Which regrets would haunt you?

Provide:
1. Analysis of each option through regret lens
2. Short-term pain vs. long-term regret trade-offs
3. Reversibility of each choice
4. Recommended decision
5. Reasoning

Respond in JSON format."""
        
        result = await ai_service.generate(prompt=prompt, mode="think")
        
        return {"analysis": result.get("output")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Regret minimization failed: {str(e)}")


@router.post("/dont-lose")
async def dont_lose_analysis(body: dict, user=Depends(firebase_auth_required)):
    """'Don't Lose' system - identify what's too important to risk"""
    situation = body.get("situation")
    
    if not situation:
        raise HTTPException(status_code=400, detail="situation required")
    
    try:
        prompt = f"""Apply "Don't Lose" framework to this situation:

Situation: {situation}

Identify:
1. What are the irreplaceable elements? (health, relationships, reputation, core values)
2. What are the "Table Stakes" - things that must be preserved?
3. What are acceptable risks vs. unacceptable risks?
4. How to achieve goals WITHOUT risking what you can't afford to lose?
5. Alternative paths that protect critical assets
6. Early warning signs you're risking too much

Respond in JSON format with clear "DO NOT RISK" items and safe paths forward."""
        
        result = await ai_service.generate(prompt=prompt, mode="think")
        
        return {"analysis": result.get("output")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Don't Lose analysis failed: {str(e)}")


@router.post("/life-simulation")
async def life_simulation(body: dict, user=Depends(firebase_auth_required)):
    """Simulate life paths based on current decisions"""
    current_age = body.get("current_age")
    current_situation = body.get("current_situation")
    decisions = body.get("decisions", [])
    
    if not current_age or not current_situation:
        raise HTTPException(status_code=400, detail="current_age and current_situation required")
    
    try:
        prompt = f"""Simulate life trajectories:

Current Age: {current_age}
Current Situation: {json.dumps(current_situation)}
Pending Decisions: {json.dumps(decisions)}

Simulate 3 scenarios (10-year projection):
1. Optimistic path - best reasonable outcomes
2. Realistic path - most likely outcomes
3. Pessimistic path - challenges and setbacks

For each scenario at 5-year and 10-year marks, describe:
- Career state
- Financial state
- Relationships
- Health & well-being
- Key life events
- Regrets/satisfactions

Include probability estimates for each scenario.

Respond in JSON format."""
        
        result = await ai_service.generate(prompt=prompt, mode="think")
        
        return {"simulation": result.get("output")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Life simulation failed: {str(e)}")


@router.get("/consequences/history")
def get_consequence_history(user=Depends(firebase_auth_required)):
    """Get consequence modeling history"""
    with Session(engine) as session:
        models = session.exec(
            select(ConsequenceModel).where(ConsequenceModel.user_id == user["uid"])
        ).all()
        
        return {"models": [m.dict() for m in models]}
