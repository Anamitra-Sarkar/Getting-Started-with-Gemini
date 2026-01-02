from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import Optional, List
from ..models import engine, LearningGap, CareerAnalysis
from ..auth.firebase import firebase_auth_required
from ..ai.service import ai_service
import json

router = APIRouter(prefix="/education", tags=["education"])


class LearningGapRequest(BaseModel):
    subject: str
    current_level: str
    target_level: str
    background: Optional[str] = None


class ResumeAnalysisRequest(BaseModel):
    resume_text: str
    job_description: Optional[str] = None


class SalaryAnalysisRequest(BaseModel):
    role: str
    experience_years: int
    location: str
    skills: List[str]


class CareerPathRequest(BaseModel):
    current_role: str
    desired_role: str
    timeframe: str = "3 years"


@router.post("/learning-gaps/detect")
async def detect_learning_gaps(body: LearningGapRequest, user=Depends(firebase_auth_required)):
    """Detect learning gaps and provide study roadmap"""
    try:
        prompt = f"""Analyze learning gaps:

Subject: {body.subject}
Current Level: {body.current_level}
Target Level: {body.target_level}
Background: {body.background or 'Not provided'}

Provide:
1. Detailed gap analysis
2. Prerequisites needed
3. Learning roadmap (ordered topics)
4. Estimated time for each topic
5. Recommended resources
6. Practice/project suggestions
7. Assessment checkpoints

Respond in JSON format."""
        
        result = await ai_service.generate(prompt=prompt, mode="study")
        
        with Session(engine) as session:
            gap_analysis = LearningGap(
                user_id=user["uid"],
                subject=body.subject,
                current_level=body.current_level,
                target_level=body.target_level,
                gaps=result.get("output", "{}"),
                recommendations=result.get("output", "{}")
            )
            session.add(gap_analysis)
            session.commit()
            session.refresh(gap_analysis)
        
        return {"analysis": result.get("output"), "analysis_id": gap_analysis.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Learning gap detection failed: {str(e)}")


@router.post("/resume/analyze")
async def analyze_resume(body: ResumeAnalysisRequest, user=Depends(firebase_auth_required)):
    """Analyze resume with ATS scoring"""
    try:
        prompt = f"""Analyze this resume:

Resume:
{body.resume_text}

{f'Job Description: {body.job_description}' if body.job_description else ''}

Provide:
1. ATS score (0-100)
2. Keyword optimization
3. Formatting issues
4. Content strengths
5. Content gaps
6. Improvement recommendations
7. Industry-specific suggestions

Respond in JSON format."""
        
        result = await ai_service.generate(prompt=prompt, mode="study")
        
        with Session(engine) as session:
            analysis = CareerAnalysis(
                user_id=user["uid"],
                analysis_type="resume",
                input_data=body.resume_text[:500],  # Store abbreviated version
                result=result.get("output", "{}")
            )
            session.add(analysis)
            session.commit()
        
        return {"analysis": result.get("output")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resume analysis failed: {str(e)}")


@router.post("/salary/analyze")
async def analyze_salary(body: SalaryAnalysisRequest, user=Depends(firebase_auth_required)):
    """Analyze salary expectations and market rates"""
    try:
        prompt = f"""Analyze salary expectations:

Role: {body.role}
Experience: {body.experience_years} years
Location: {body.location}
Skills: {', '.join(body.skills)}

Provide:
1. Market salary range (min, median, max)
2. Factors affecting compensation
3. Negotiation leverage points
4. Skills that increase value
5. Career growth impact on salary
6. Location adjustments
7. Total compensation considerations

Respond in JSON format."""
        
        result = await ai_service.generate(prompt=prompt, mode="think")
        
        with Session(engine) as session:
            analysis = CareerAnalysis(
                user_id=user["uid"],
                analysis_type="salary",
                input_data=json.dumps({"role": body.role, "experience": body.experience_years}),
                result=result.get("output", "{}")
            )
            session.add(analysis)
            session.commit()
        
        return {"analysis": result.get("output")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Salary analysis failed: {str(e)}")


@router.post("/career/path")
async def analyze_career_path(body: CareerPathRequest, user=Depends(firebase_auth_required)):
    """Analyze career path and provide roadmap"""
    try:
        prompt = f"""Create career path roadmap:

Current Role: {body.current_role}
Desired Role: {body.desired_role}
Timeframe: {body.timeframe}

Provide:
1. Gap analysis (skills, experience, network)
2. Intermediate milestones
3. Required skills to develop
4. Certifications or education needed
5. Experience to gain
6. Networking strategy
7. Timeline with checkpoints
8. Risk mitigation

Respond in JSON format."""
        
        result = await ai_service.generate(prompt=prompt, mode="study")
        
        with Session(engine) as session:
            analysis = CareerAnalysis(
                user_id=user["uid"],
                analysis_type="path",
                input_data=json.dumps({"current": body.current_role, "desired": body.desired_role}),
                result=result.get("output", "{}")
            )
            session.add(analysis)
            session.commit()
        
        return {"roadmap": result.get("output")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Career path analysis failed: {str(e)}")


@router.post("/skills/gap")
async def analyze_skill_gaps(body: dict, user=Depends(firebase_auth_required)):
    """Analyze skill gaps for target role"""
    current_skills = body.get("current_skills", [])
    target_role = body.get("target_role")
    
    if not target_role:
        raise HTTPException(status_code=400, detail="target_role required")
    
    try:
        prompt = f"""Analyze skill gaps:

Current Skills: {', '.join(current_skills)}
Target Role: {target_role}

Provide:
1. Required skills for target role
2. Skill gaps to address
3. Priority order for learning
4. Learning resources for each skill
5. Expected time to proficiency
6. Projects to demonstrate skills

Respond in JSON format."""
        
        result = await ai_service.generate(prompt=prompt, mode="study")
        
        return {"gap_analysis": result.get("output")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Skill gap analysis failed: {str(e)}")


@router.post("/interview/prepare")
async def prepare_interview(body: dict, user=Depends(firebase_auth_required)):
    """Generate interview preparation plan"""
    role = body.get("role")
    company = body.get("company")
    
    if not role:
        raise HTTPException(status_code=400, detail="role required")
    
    try:
        prompt = f"""Create interview preparation plan:

Role: {role}
{f'Company: {company}' if company else ''}

Provide:
1. Common interview questions for this role
2. Technical topics to review
3. Behavioral question preparation
4. Company research points
5. Questions to ask interviewer
6. Red flags to watch for
7. Preparation timeline (1-2 weeks)

Respond in JSON format."""
        
        result = await ai_service.generate(prompt=prompt, mode="study")
        
        return {"preparation_plan": result.get("output")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Interview preparation failed: {str(e)}")


@router.get("/analysis/history")
def get_career_history(
    analysis_type: Optional[str] = None,
    user=Depends(firebase_auth_required)
):
    """Get career analysis history"""
    with Session(engine) as session:
        query = select(CareerAnalysis).where(CareerAnalysis.user_id == user["uid"])
        
        if analysis_type:
            query = query.where(CareerAnalysis.analysis_type == analysis_type)
        
        analyses = session.exec(query).all()
        
        return {"analyses": [a.dict() for a in analyses]}
