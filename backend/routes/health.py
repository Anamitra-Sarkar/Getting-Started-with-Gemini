from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import Optional, List
from ..models import engine, HealthAnalysis
from ..auth.firebase import firebase_auth_required
from ..ai.service import ai_service
import json

router = APIRouter(prefix="/health", tags=["health"])


class WellnessAnalysisRequest(BaseModel):
    data: dict  # sleep, exercise, nutrition, stress levels


class LongevityAnalysisRequest(BaseModel):
    age: int
    lifestyle_factors: dict
    health_metrics: Optional[dict] = None


class NutritionAnalysisRequest(BaseModel):
    diet_log: List[dict]
    goals: Optional[List[str]] = None


class FitnessAnalysisRequest(BaseModel):
    current_fitness: dict
    goals: List[str]


@router.post("/wellness/analyze")
async def analyze_wellness(body: WellnessAnalysisRequest, user=Depends(firebase_auth_required)):
    """Analyze overall wellness trends and provide recommendations"""
    try:
        prompt = f"""Analyze wellness data and provide comprehensive recommendations:

Data:
{json.dumps(body.data, indent=2)}

Provide:
1. Overall wellness score
2. Key strengths
3. Areas for improvement
4. Actionable recommendations
5. Trend analysis
6. Warning signs if any

Respond in JSON format."""
        
        result = await ai_service.generate(prompt=prompt, mode="study")
        
        with Session(engine) as session:
            analysis = HealthAnalysis(
                user_id=user["uid"],
                analysis_type="wellness",
                input_data=json.dumps(body.data),
                recommendations=result.get("output", "{}")
            )
            session.add(analysis)
            session.commit()
            session.refresh(analysis)
        
        return {"analysis": result.get("output"), "analysis_id": analysis.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Wellness analysis failed: {str(e)}")


@router.post("/longevity/analyze")
async def analyze_longevity(body: LongevityAnalysisRequest, user=Depends(firebase_auth_required)):
    """Analyze longevity factors and provide optimization recommendations"""
    try:
        prompt = f"""Analyze longevity potential based on:

Age: {body.age}
Lifestyle Factors: {json.dumps(body.lifestyle_factors)}
Health Metrics: {json.dumps(body.health_metrics or {})}

Provide:
1. Longevity score
2. Key positive factors
3. Key risk factors
4. Optimization recommendations
5. Lifestyle interventions
6. Monitoring suggestions

Respond in JSON format."""
        
        result = await ai_service.generate(prompt=prompt, mode="think")
        
        with Session(engine) as session:
            analysis = HealthAnalysis(
                user_id=user["uid"],
                analysis_type="longevity",
                input_data=json.dumps({"age": body.age, "lifestyle": body.lifestyle_factors}),
                recommendations=result.get("output", "{}")
            )
            session.add(analysis)
            session.commit()
        
        return {"analysis": result.get("output")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Longevity analysis failed: {str(e)}")


@router.post("/nutrition/analyze")
async def analyze_nutrition(body: NutritionAnalysisRequest, user=Depends(firebase_auth_required)):
    """Analyze nutrition patterns and provide recommendations"""
    try:
        prompt = f"""Analyze nutrition data:

Diet Log:
{json.dumps(body.diet_log, indent=2)}

Goals: {', '.join(body.goals) if body.goals else 'General health'}

Provide:
1. Nutritional balance assessment
2. Macro and micronutrient analysis
3. Gaps and deficiencies
4. Recommendations
5. Meal planning suggestions

Respond in JSON format."""
        
        result = await ai_service.generate(prompt=prompt, mode="study")
        
        with Session(engine) as session:
            analysis = HealthAnalysis(
                user_id=user["uid"],
                analysis_type="nutrition",
                input_data=json.dumps(body.diet_log),
                recommendations=result.get("output", "{}")
            )
            session.add(analysis)
            session.commit()
        
        return {"analysis": result.get("output")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Nutrition analysis failed: {str(e)}")


@router.post("/fitness/plan")
async def create_fitness_plan(body: FitnessAnalysisRequest, user=Depends(firebase_auth_required)):
    """Create personalized fitness plan"""
    try:
        prompt = f"""Create a personalized fitness plan:

Current Fitness Level:
{json.dumps(body.current_fitness, indent=2)}

Goals: {', '.join(body.goals)}

Provide:
1. Assessment of current state
2. Realistic goal timeline
3. Weekly workout plan
4. Progressive overload strategy
5. Recovery recommendations
6. Nutrition integration
7. Progress tracking metrics

Respond in JSON format."""
        
        result = await ai_service.generate(prompt=prompt, mode="study")
        
        with Session(engine) as session:
            analysis = HealthAnalysis(
                user_id=user["uid"],
                analysis_type="fitness",
                input_data=json.dumps(body.current_fitness),
                recommendations=result.get("output", "{}")
            )
            session.add(analysis)
            session.commit()
        
        return {"plan": result.get("output")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fitness planning failed: {str(e)}")


@router.post("/research/simplify")
async def simplify_research(body: dict, user=Depends(firebase_auth_required)):
    """Simplify research papers for easier understanding"""
    paper_text = body.get("paper_text")
    paper_url = body.get("paper_url")
    
    if not paper_text and not paper_url:
        raise HTTPException(status_code=400, detail="paper_text or paper_url required")
    
    try:
        prompt = f"""Simplify this research paper for a general audience:

{paper_text or f'Paper URL: {paper_url}'}

Provide:
1. Executive summary (2-3 sentences)
2. Key findings in plain language
3. Methodology explained simply
4. Practical implications
5. Limitations and caveats
6. Related research areas

Respond in JSON format."""
        
        result = await ai_service.generate(prompt=prompt, mode="study")
        
        return {"simplified": result.get("output")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Research simplification failed: {str(e)}")


@router.get("/analysis/history")
def get_health_history(
    analysis_type: Optional[str] = None,
    user=Depends(firebase_auth_required)
):
    """Get health analysis history"""
    with Session(engine) as session:
        query = select(HealthAnalysis).where(HealthAnalysis.user_id == user["uid"])
        
        if analysis_type:
            query = query.where(HealthAnalysis.analysis_type == analysis_type)
        
        analyses = session.exec(query).all()
        
        return {"analyses": [a.dict() for a in analyses]}
