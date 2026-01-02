from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import Optional, List
from ..models import engine, MarketAnalysis, PortfolioRisk
from ..auth.firebase import firebase_auth_required
from ..ai.service import ai_service
import json

router = APIRouter(prefix="/markets", tags=["markets"])


class EarningsAnalysisRequest(BaseModel):
    symbol: str
    earnings_data: Optional[dict] = None


class SectorRotationRequest(BaseModel):
    sectors: List[str]
    timeframe: str = "quarterly"


class MacroSimulationRequest(BaseModel):
    scenario: str
    variables: dict


class CryptoRiskRequest(BaseModel):
    token: str
    address: Optional[str] = None


class PortfolioAnalysisRequest(BaseModel):
    holdings: List[dict]  # [{symbol, quantity, cost_basis}]


@router.post("/earnings/analyze")
async def analyze_earnings(body: EarningsAnalysisRequest, user=Depends(firebase_auth_required)):
    """Analyze earnings report and provide insights"""
    try:
        prompt = f"""Analyze the earnings report for {body.symbol}.

Provide:
1. Key highlights
2. Revenue trends
3. Profitability metrics
4. Guidance analysis
5. Risk factors
6. Investment recommendation

Respond in JSON format."""
        
        result = await ai_service.generate(prompt=prompt, mode="study")
        
        # Store the analysis
        with Session(engine) as session:
            analysis = MarketAnalysis(
                user_id=user["uid"],
                symbol=body.symbol,
                analysis_type="earnings",
                data=result.get("output", "{}")
            )
            session.add(analysis)
            session.commit()
            session.refresh(analysis)
        
        return {"analysis": result.get("output"), "analysis_id": analysis.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Earnings analysis failed: {str(e)}")


@router.post("/sector/rotation")
async def analyze_sector_rotation(body: SectorRotationRequest, user=Depends(firebase_auth_required)):
    """Analyze sector rotation trends"""
    try:
        prompt = f"""Analyze sector rotation for: {', '.join(body.sectors)}
Timeframe: {body.timeframe}

Identify:
1. Which sectors are strengthening
2. Which sectors are weakening
3. Key drivers of rotation
4. Recommended positioning

Respond in JSON format."""
        
        result = await ai_service.generate(prompt=prompt, mode="think")
        
        with Session(engine) as session:
            analysis = MarketAnalysis(
                user_id=user["uid"],
                symbol="SECTORS",
                analysis_type="sector",
                data=result.get("output", "{}")
            )
            session.add(analysis)
            session.commit()
        
        return {"analysis": result.get("output")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sector rotation analysis failed: {str(e)}")


@router.post("/macro/simulate")
async def simulate_macro(body: MacroSimulationRequest, user=Depends(firebase_auth_required)):
    """Simulate macroeconomic scenarios"""
    try:
        prompt = f"""Simulate this macroeconomic scenario:

Scenario: {body.scenario}
Variables: {json.dumps(body.variables)}

Analyze:
1. Impact on GDP
2. Impact on inflation
3. Impact on employment
4. Impact on markets
5. Policy implications

Respond in JSON format."""
        
        result = await ai_service.generate(prompt=prompt, mode="think")
        
        with Session(engine) as session:
            analysis = MarketAnalysis(
                user_id=user["uid"],
                symbol="MACRO",
                analysis_type="macro",
                data=result.get("output", "{}")
            )
            session.add(analysis)
            session.commit()
        
        return {"simulation": result.get("output")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Macro simulation failed: {str(e)}")


@router.post("/crypto/risk")
async def analyze_crypto_risk(body: CryptoRiskRequest, user=Depends(firebase_auth_required)):
    """Analyze cryptocurrency risks including scam detection"""
    try:
        prompt = f"""Analyze risks for cryptocurrency: {body.token}
Contract Address: {body.address or 'Not provided'}

Check for:
1. Scam indicators (honeypot, rug pull risks)
2. Liquidity risks
3. Smart contract risks
4. Team and governance risks
5. Market manipulation risks
6. Overall risk score (0-10)

Respond in JSON format."""
        
        result = await ai_service.generate(prompt=prompt, mode="think")
        
        with Session(engine) as session:
            analysis = MarketAnalysis(
                user_id=user["uid"],
                symbol=body.token,
                analysis_type="risk",
                data=result.get("output", "{}")
            )
            session.add(analysis)
            session.commit()
        
        return {"risk_analysis": result.get("output")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Crypto risk analysis failed: {str(e)}")


@router.post("/defi/analyze")
async def analyze_defi(body: dict, user=Depends(firebase_auth_required)):
    """Analyze DeFi protocols and opportunities"""
    protocol = body.get("protocol")
    
    if not protocol:
        raise HTTPException(status_code=400, detail="protocol required")
    
    try:
        prompt = f"""Analyze DeFi protocol: {protocol}

Evaluate:
1. TVL (Total Value Locked) trends
2. Yield opportunities
3. Smart contract audit status
4. Risk assessment
5. Competitive positioning

Respond in JSON format."""
        
        result = await ai_service.generate(prompt=prompt, mode="study")
        
        return {"analysis": result.get("output")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DeFi analysis failed: {str(e)}")


@router.post("/portfolio/analyze")
async def analyze_portfolio(body: PortfolioAnalysisRequest, user=Depends(firebase_auth_required)):
    """Analyze portfolio for risk and optimization opportunities"""
    try:
        prompt = f"""Analyze this investment portfolio:

Holdings:
{json.dumps(body.holdings, indent=2)}

Provide:
1. Diversification score
2. Risk assessment
3. Concentration risks
4. Correlation analysis
5. Optimization recommendations
6. Overall portfolio health score

Respond in JSON format."""
        
        result = await ai_service.generate(prompt=prompt, mode="think")
        
        try:
            analysis_data = json.loads(result.get("output", "{}"))
            risk_score = float(analysis_data.get("risk_score", 5.0))
        except:
            analysis_data = {}
            risk_score = 5.0
        
        # Store portfolio risk analysis
        with Session(engine) as session:
            portfolio_risk = PortfolioRisk(
                user_id=user["uid"],
                portfolio_data=json.dumps(body.holdings),
                risk_score=risk_score,
                recommendations=result.get("output", "{}")
            )
            session.add(portfolio_risk)
            session.commit()
            session.refresh(portfolio_risk)
        
        return {
            "analysis": result.get("output"),
            "analysis_id": portfolio_risk.id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Portfolio analysis failed: {str(e)}")


@router.get("/analysis/history")
def get_analysis_history(
    analysis_type: Optional[str] = None,
    user=Depends(firebase_auth_required)
):
    """Get market analysis history"""
    with Session(engine) as session:
        query = select(MarketAnalysis).where(MarketAnalysis.user_id == user["uid"])
        
        if analysis_type:
            query = query.where(MarketAnalysis.analysis_type == analysis_type)
        
        analyses = session.exec(query).all()
        
        return {"analyses": [a.dict() for a in analyses]}
