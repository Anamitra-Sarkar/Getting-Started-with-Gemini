from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import Optional, List
from ..models import engine, BusinessAnalysis
from ..auth.firebase import firebase_auth_required
from ..ai.service import ai_service
import json

router = APIRouter(prefix="/business", tags=["business"])


class MarketSizingRequest(BaseModel):
    product: str
    market: str
    geography: Optional[str] = None


class CompetitiveMoatRequest(BaseModel):
    company: str
    industry: str


class PricingSimulationRequest(BaseModel):
    product: str
    cost_structure: dict
    target_margin: float
    competition: Optional[List[dict]] = None


class GTMPlanRequest(BaseModel):
    product: str
    target_market: str
    budget: Optional[float] = None


class SWOTRequest(BaseModel):
    company: str
    context: Optional[str] = None


@router.post("/market-sizing")
async def calculate_market_sizing(body: MarketSizingRequest, user=Depends(firebase_auth_required)):
    """Calculate total addressable market (TAM), SAM, and SOM"""
    try:
        prompt = f"""Calculate market sizing:

Product: {body.product}
Market: {body.market}
Geography: {body.geography or 'Global'}

Provide:
1. TAM (Total Addressable Market)
2. SAM (Serviceable Addressable Market)
3. SOM (Serviceable Obtainable Market)
4. Methodology and assumptions
5. Market growth rate
6. Key market drivers
7. Validation sources

Respond in JSON format with numerical estimates."""
        
        result = await ai_service.generate(prompt=prompt, mode="think")
        
        with Session(engine) as session:
            analysis = BusinessAnalysis(
                user_id=user["uid"],
                analysis_type="market_sizing",
                input_data=json.dumps({"product": body.product, "market": body.market}),
                result=result.get("output", "{}")
            )
            session.add(analysis)
            session.commit()
            session.refresh(analysis)
        
        return {"sizing": result.get("output"), "analysis_id": analysis.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Market sizing failed: {str(e)}")


@router.post("/moat/analyze")
async def analyze_competitive_moat(body: CompetitiveMoatRequest, user=Depends(firebase_auth_required)):
    """Analyze competitive moat and defensibility"""
    try:
        prompt = f"""Analyze competitive moat:

Company: {body.company}
Industry: {body.industry}

Evaluate these moat types:
1. Network effects
2. Switching costs
3. Brand strength
4. Proprietary technology
5. Cost advantages
6. Regulatory barriers
7. Data/knowledge advantages

For each:
- Strength (0-10)
- Durability
- Evidence
- Risks

Provide overall moat score and sustainability assessment.

Respond in JSON format."""
        
        result = await ai_service.generate(prompt=prompt, mode="think")
        
        with Session(engine) as session:
            analysis = BusinessAnalysis(
                user_id=user["uid"],
                analysis_type="moat",
                input_data=json.dumps({"company": body.company}),
                result=result.get("output", "{}")
            )
            session.add(analysis)
            session.commit()
        
        return {"moat_analysis": result.get("output")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Moat analysis failed: {str(e)}")


@router.post("/pricing/simulate")
async def simulate_pricing(body: PricingSimulationRequest, user=Depends(firebase_auth_required)):
    """Simulate pricing strategies"""
    try:
        prompt = f"""Simulate pricing strategies:

Product: {body.product}
Cost Structure: {json.dumps(body.cost_structure)}
Target Margin: {body.target_margin * 100}%
Competition: {json.dumps(body.competition) if body.competition else 'Not specified'}

Analyze:
1. Cost-plus pricing
2. Value-based pricing
3. Competition-based pricing
4. Penetration pricing
5. Premium pricing

For each strategy provide:
- Recommended price point
- Expected volume impact
- Revenue projection
- Market positioning
- Risk factors

Recommend optimal strategy.

Respond in JSON format."""
        
        result = await ai_service.generate(prompt=prompt, mode="think")
        
        with Session(engine) as session:
            analysis = BusinessAnalysis(
                user_id=user["uid"],
                analysis_type="pricing",
                input_data=json.dumps({"product": body.product, "margin": body.target_margin}),
                result=result.get("output", "{}")
            )
            session.add(analysis)
            session.commit()
        
        return {"pricing_simulation": result.get("output")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pricing simulation failed: {str(e)}")


@router.post("/gtm/plan")
async def create_gtm_plan(body: GTMPlanRequest, user=Depends(firebase_auth_required)):
    """Create go-to-market plan"""
    try:
        prompt = f"""Create comprehensive GTM plan:

Product: {body.product}
Target Market: {body.target_market}
Budget: {f'${body.budget:,.2f}' if body.budget else 'Not specified'}

Provide:
1. Market segmentation
2. Customer personas
3. Value proposition
4. Channel strategy
5. Marketing mix (4 Ps)
6. Sales strategy
7. Launch timeline (phases)
8. Success metrics
9. Budget allocation
10. Risk mitigation

Respond in JSON format."""
        
        result = await ai_service.generate(prompt=prompt, mode="study")
        
        with Session(engine) as session:
            analysis = BusinessAnalysis(
                user_id=user["uid"],
                analysis_type="gtm",
                input_data=json.dumps({"product": body.product, "market": body.target_market}),
                result=result.get("output", "{}")
            )
            session.add(analysis)
            session.commit()
        
        return {"gtm_plan": result.get("output")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GTM planning failed: {str(e)}")


@router.post("/swot")
async def swot_analysis(body: SWOTRequest, user=Depends(firebase_auth_required)):
    """Perform SWOT analysis"""
    try:
        prompt = f"""Perform SWOT analysis:

Company: {body.company}
Context: {body.context or 'General analysis'}

Provide comprehensive analysis:

Strengths:
- Internal capabilities
- Resources
- Competitive advantages

Weaknesses:
- Internal limitations
- Resource gaps
- Vulnerabilities

Opportunities:
- Market trends
- Growth areas
- Strategic moves

Threats:
- Competition
- Market changes
- External risks

For each item, provide:
- Description
- Impact level (High/Medium/Low)
- Actionability

Include strategic recommendations.

Respond in JSON format."""
        
        result = await ai_service.generate(prompt=prompt, mode="think")
        
        with Session(engine) as session:
            analysis = BusinessAnalysis(
                user_id=user["uid"],
                analysis_type="swot",
                input_data=json.dumps({"company": body.company}),
                result=result.get("output", "{}")
            )
            session.add(analysis)
            session.commit()
        
        return {"swot": result.get("output")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SWOT analysis failed: {str(e)}")


@router.post("/business-model")
async def business_model_canvas(body: dict, user=Depends(firebase_auth_required)):
    """Create business model canvas"""
    company = body.get("company")
    
    if not company:
        raise HTTPException(status_code=400, detail="company required")
    
    try:
        prompt = f"""Create Business Model Canvas for: {company}

Analyze and structure:
1. Customer Segments
2. Value Propositions
3. Channels
4. Customer Relationships
5. Revenue Streams
6. Key Resources
7. Key Activities
8. Key Partnerships
9. Cost Structure

For each component:
- Detailed description
- Strategic importance
- Interdependencies

Respond in JSON format."""
        
        result = await ai_service.generate(prompt=prompt, mode="think")
        
        return {"business_model": result.get("output")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Business model canvas failed: {str(e)}")


@router.post("/financial-projection")
async def financial_projection(body: dict, user=Depends(firebase_auth_required)):
    """Create financial projections"""
    business_data = body.get("business_data")
    timeframe = body.get("timeframe", "5 years")
    
    if not business_data:
        raise HTTPException(status_code=400, detail="business_data required")
    
    try:
        prompt = f"""Create financial projections:

Business Data: {json.dumps(business_data)}
Timeframe: {timeframe}

Provide:
1. Revenue projections (by year)
2. Cost projections
3. Gross margin
4. Operating expenses
5. EBITDA
6. Cash flow analysis
7. Break-even analysis
8. Assumptions and scenarios (best/base/worst)

Respond in JSON format with numerical projections."""
        
        result = await ai_service.generate(prompt=prompt, mode="think")
        
        with Session(engine) as session:
            analysis = BusinessAnalysis(
                user_id=user["uid"],
                analysis_type="financial",
                input_data=json.dumps(business_data),
                result=result.get("output", "{}")
            )
            session.add(analysis)
            session.commit()
        
        return {"projections": result.get("output")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Financial projection failed: {str(e)}")


@router.get("/analysis/history")
def get_business_history(
    analysis_type: Optional[str] = None,
    user=Depends(firebase_auth_required)
):
    """Get business analysis history"""
    with Session(engine) as session:
        query = select(BusinessAnalysis).where(BusinessAnalysis.user_id == user["uid"])
        
        if analysis_type:
            query = query.where(BusinessAnalysis.analysis_type == analysis_type)
        
        analyses = session.exec(query).all()
        
        return {"analyses": [a.dict() for a in analyses]}
