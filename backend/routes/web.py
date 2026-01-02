from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import Optional, List
from ..models import engine, CredibilityScore, Citation
from ..auth.firebase import firebase_auth_required
from ..ai.service import ai_service
from ..search.tavily import tavily_search
import json
from urllib.parse import urlparse

router = APIRouter(prefix="/web", tags=["web"])


class WebSummarizeRequest(BaseModel):
    url: Optional[str] = None
    query: Optional[str] = None
    max_sources: int = 5


class BiasCheckRequest(BaseModel):
    url: Optional[str] = None
    text: Optional[str] = None


class NewsHeatmapRequest(BaseModel):
    topics: List[str]
    timeframe: str = "24h"


@router.post("/summarize")
async def summarize_web(body: WebSummarizeRequest, user=Depends(firebase_auth_required)):
    """Live web summarization with citation"""
    try:
        if not body.url and not body.query:
            raise HTTPException(status_code=400, detail="url or query required")
        
        # Search for sources if query provided
        sources = []
        if body.query:
            search_results = await tavily_search(body.query)
            sources = search_results.get("results", [])[:body.max_sources]
        elif body.url:
            # Fetch and analyze single URL
            sources = [{"url": body.url}]
        
        # Summarize sources
        source_texts = "\n\n".join([
            f"Source {i+1} ({s.get('url', 'unknown')}):\n{s.get('content', s.get('snippet', ''))}"
            for i, s in enumerate(sources)
        ])
        
        prompt = f"""Summarize these web sources comprehensively:

{source_texts}

Provide:
1. Executive summary
2. Key points (bullet points)
3. Different perspectives if multiple sources
4. Credibility assessment
5. Citations (which source for which claim)
6. What's missing or unclear

Respond in JSON format."""
        
        result = await ai_service.generate(prompt=prompt, mode="study", sources=sources)
        
        return {
            "summary": result.get("output"),
            "sources": sources,
            "source_count": len(sources)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Web summarization failed: {str(e)}")


@router.post("/credibility/check")
async def check_credibility(body: BiasCheckRequest, user=Depends(firebase_auth_required)):
    """Check credibility of source or content"""
    try:
        if not body.url and not body.text:
            raise HTTPException(status_code=400, detail="url or text required")
        
        target = body.url or body.text[:500]
        
        # Check domain reputation if URL provided
        domain_score = 0.5
        if body.url:
            domain = urlparse(body.url).netloc
            
            # Check if we have cached credibility score
            with Session(engine) as session:
                cached = session.exec(
                    select(CredibilityScore).where(CredibilityScore.domain == domain)
                ).first()
                
                if cached:
                    domain_score = cached.score
        
        # AI-based credibility analysis
        prompt = f"""Assess credibility:

{'URL: ' + body.url if body.url else ''}
{'Content: ' + body.text if body.text else ''}

Evaluate:
1. Source authority (expertise, reputation)
2. Evidence quality (citations, data)
3. Transparency (author, funding, conflicts)
4. Consistency (with known facts)
5. Recency (is information current?)
6. Bias indicators

Provide:
- Overall credibility score (0-1)
- Confidence in assessment
- Key factors (positive and negative)
- Red flags if any
- Fact-check suggestions

Respond in JSON format."""
        
        result = await ai_service.generate(prompt=prompt, mode="think")
        
        try:
            analysis = json.loads(result.get("output", "{}"))
            overall_score = float(analysis.get("credibility_score", 0.5))
        except:
            analysis = {}
            overall_score = 0.5
        
        # Cache domain score if URL
        if body.url:
            domain = urlparse(body.url).netloc
            with Session(engine) as session:
                # Update or create credibility score
                existing = session.exec(
                    select(CredibilityScore).where(CredibilityScore.url == body.url)
                ).first()
                
                if existing:
                    existing.score = overall_score
                    existing.factors = json.dumps(analysis)
                    session.add(existing)
                else:
                    cred = CredibilityScore(
                        url=body.url,
                        domain=domain,
                        score=overall_score,
                        factors=json.dumps(analysis)
                    )
                    session.add(cred)
                session.commit()
        
        return {
            "credibility_score": overall_score,
            "domain_score": domain_score,
            "analysis": analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Credibility check failed: {str(e)}")


@router.post("/bias/detect")
async def detect_web_bias(body: BiasCheckRequest, user=Depends(firebase_auth_required)):
    """Detect bias in web content or sources"""
    try:
        if not body.url and not body.text:
            raise HTTPException(status_code=400, detail="url or text required")
        
        content = body.text or f"Content from: {body.url}"
        
        prompt = f"""Detect bias in this content:

{content}

Analyze for:
1. Political bias (left/center/right)
2. Selection bias (what's emphasized/omitted)
3. Framing bias (word choice, tone)
4. Source bias (who is quoted/cited)
5. Confirmation bias (cherry-picking)

For each bias found:
- Type
- Severity (low/medium/high)
- Evidence
- Impact on credibility

Provide:
- Overall bias score (-1 to 1, where -1=left, 0=center, 1=right)
- Objectivity score (0-1)
- Recommendations for balanced perspective

Respond in JSON format."""
        
        result = await ai_service.generate(prompt=prompt, mode="think")
        
        return {"bias_analysis": result.get("output")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bias detection failed: {str(e)}")


@router.post("/news/heatmap")
async def news_heatmap(body: NewsHeatmapRequest, user=Depends(firebase_auth_required)):
    """Generate news heatmap showing coverage intensity"""
    try:
        # Search for each topic
        topic_results = {}
        for topic in body.topics:
            results = await tavily_search(topic)
            topic_results[topic] = {
                "result_count": len(results.get("results", [])),
                "sources": results.get("results", [])[:5]
            }
        
        # Analyze coverage patterns
        prompt = f"""Analyze news coverage patterns:

Topics and Results:
{json.dumps(topic_results, indent=2)}

Timeframe: {body.timeframe}

Provide:
1. Coverage intensity for each topic (0-10)
2. Trending topics
3. Underreported topics
4. Geographic distribution of coverage
5. Source diversity
6. Narrative patterns

Respond in JSON format suitable for visualization."""
        
        result = await ai_service.generate(prompt=prompt, mode="think")
        
        return {
            "heatmap": result.get("output"),
            "raw_data": topic_results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"News heatmap generation failed: {str(e)}")


@router.post("/narrative/shifts")
async def detect_narrative_shifts(body: dict, user=Depends(firebase_auth_required)):
    """Detect shifts in narrative around a topic"""
    topic = body.get("topic")
    
    if not topic:
        raise HTTPException(status_code=400, detail="topic required")
    
    try:
        # Search for recent coverage
        results = await tavily_search(topic)
        sources = results.get("results", [])[:10]
        
        prompt = f"""Detect narrative shifts for topic: {topic}

Recent Sources:
{json.dumps(sources, indent=2)}

Analyze:
1. Current dominant narrative
2. Emerging counter-narratives
3. Shift in framing over time
4. Change in key players/voices
5. Evolution of public sentiment
6. Triggers for narrative change

Provide timeline of shifts and key inflection points.

Respond in JSON format."""
        
        result = await ai_service.generate(prompt=prompt, mode="think")
        
        return {"narrative_analysis": result.get("output")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Narrative shift detection failed: {str(e)}")


@router.post("/fact-check")
async def fact_check(body: dict, user=Depends(firebase_auth_required)):
    """Fact-check a claim using web sources"""
    claim = body.get("claim")
    
    if not claim:
        raise HTTPException(status_code=400, detail="claim required")
    
    try:
        # Search for fact-checks and related information
        search_query = f"fact check {claim}"
        results = await tavily_search(search_query)
        sources = results.get("results", [])
        
        prompt = f"""Fact-check this claim:

Claim: {claim}

Sources Found:
{json.dumps(sources, indent=2)}

Provide:
1. Verdict (True/False/Partially True/Unverifiable)
2. Confidence level (0-1)
3. Supporting evidence
4. Contradicting evidence
5. Context needed
6. Authoritative sources consulted
7. Explanation

Respond in JSON format."""
        
        result = await ai_service.generate(prompt=prompt, mode="think", sources=sources)
        
        return {
            "fact_check": result.get("output"),
            "sources": sources
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fact-checking failed: {str(e)}")


@router.get("/credibility/history")
def get_credibility_history(domain: Optional[str] = None, user=Depends(firebase_auth_required)):
    """Get credibility check history"""
    with Session(engine) as session:
        query = select(CredibilityScore)
        
        if domain:
            query = query.where(CredibilityScore.domain == domain)
        
        scores = session.exec(query).all()
        
        return {"scores": [s.dict() for s in scores]}
