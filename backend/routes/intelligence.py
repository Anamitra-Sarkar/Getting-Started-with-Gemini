from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import Optional, List
from ..models import engine, IntentAnalysis, BiasDetection, DecisionAnalysis
from ..auth.firebase import firebase_auth_required
from ..ai.service import ai_service
import json

router = APIRouter(prefix="/intelligence", tags=["intelligence"])


class IntentDetectionRequest(BaseModel):
    text: str
    conversation_id: Optional[int] = None
    message_id: Optional[int] = None


class BiasDetectionRequest(BaseModel):
    content: str
    content_type: str = "message"
    content_id: Optional[int] = None


class DecisionAnalysisRequest(BaseModel):
    decision_context: str
    options: Optional[List[str]] = None


@router.post("/intent/detect")
async def detect_intent(body: IntentDetectionRequest, user=Depends(firebase_auth_required)):
    """Detect intent from user input with confidence scoring"""
    try:
        # Use AI service to analyze intent
        prompt = f"""Analyze the following text and determine the user's intent.
Provide:
1. Primary intent (1-3 words)
2. Confidence score (0-1)
3. Ambiguity score (0-1, higher means more ambiguous)
4. Alternative interpretations if ambiguous

Text: {body.text}

Respond in JSON format."""
        
        result = await ai_service.generate(prompt=prompt, mode="think")
        
        # Parse the result (simplified - real implementation would be more robust)
        try:
            analysis = json.loads(result.get("output", "{}"))
        except:
            analysis = {
                "intent": "general_query",
                "confidence": 0.7,
                "ambiguity": 0.3,
                "suggestions": []
            }
        
        # Store the analysis
        with Session(engine) as session:
            intent_record = IntentAnalysis(
                conversation_id=body.conversation_id or 0,
                message_id=body.message_id or 0,
                detected_intent=analysis.get("intent", "unknown"),
                confidence=float(analysis.get("confidence", 0.7)),
                ambiguity_score=float(analysis.get("ambiguity", 0.3)),
                suggestions=json.dumps(analysis.get("suggestions", []))
            )
            session.add(intent_record)
            session.commit()
            session.refresh(intent_record)
        
        return {
            "intent": analysis.get("intent"),
            "confidence": analysis.get("confidence"),
            "ambiguity": analysis.get("ambiguity"),
            "suggestions": analysis.get("suggestions", []),
            "analysis_id": intent_record.id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Intent detection failed: {str(e)}")


@router.post("/bias/detect")
async def detect_bias(body: BiasDetectionRequest, user=Depends(firebase_auth_required)):
    """Detect cognitive biases in content"""
    try:
        prompt = f"""Analyze the following content for cognitive biases.
Identify any of these biases present:
- Confirmation bias
- Anchoring bias
- Availability bias
- Dunning-Kruger effect
- Sunk cost fallacy
- Survivorship bias

Content: {body.content}

For each bias found, provide:
1. Bias type
2. Confidence (0-1)
3. Brief explanation

Respond in JSON format with array of biases."""
        
        result = await ai_service.generate(prompt=prompt, mode="think")
        
        try:
            biases = json.loads(result.get("output", "[]"))
            if not isinstance(biases, list):
                biases = []
        except:
            biases = []
        
        # Store detected biases
        with Session(engine) as session:
            bias_records = []
            for bias in biases:
                bias_record = BiasDetection(
                    content_type=body.content_type,
                    content_id=body.content_id or 0,
                    bias_type=bias.get("type", "unknown"),
                    confidence=float(bias.get("confidence", 0.5)),
                    explanation=bias.get("explanation")
                )
                session.add(bias_record)
                bias_records.append(bias_record)
            
            session.commit()
        
        return {
            "biases_detected": len(biases),
            "biases": biases
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bias detection failed: {str(e)}")


@router.post("/decision/analyze")
async def analyze_decision(body: DecisionAnalysisRequest, user=Depends(firebase_auth_required)):
    """Analyze a decision for blind spots, second-order effects, and biases"""
    try:
        prompt = f"""Perform a comprehensive decision analysis on the following:

Decision Context: {body.decision_context}
Options: {', '.join(body.options) if body.options else 'Not specified'}

Analyze for:
1. Blind spots - What might be overlooked?
2. Second-order effects - What are the downstream consequences?
3. Cognitive biases - What biases might affect this decision?
4. Recommendation - What course of action is recommended?

Respond in JSON format with these keys: blind_spots (array), second_order_effects (array), cognitive_biases (array), recommendation (string)."""
        
        result = await ai_service.generate(prompt=prompt, mode="think")
        
        try:
            analysis = json.loads(result.get("output", "{}"))
        except:
            analysis = {
                "blind_spots": [],
                "second_order_effects": [],
                "cognitive_biases": [],
                "recommendation": "Unable to analyze at this time"
            }
        
        # Store the analysis
        with Session(engine) as session:
            decision_record = DecisionAnalysis(
                user_id=user["uid"],
                decision_context=body.decision_context,
                blind_spots=json.dumps(analysis.get("blind_spots", [])),
                second_order_effects=json.dumps(analysis.get("second_order_effects", [])),
                cognitive_biases=json.dumps(analysis.get("cognitive_biases", [])),
                recommendation=analysis.get("recommendation")
            )
            session.add(decision_record)
            session.commit()
            session.refresh(decision_record)
        
        return {
            "analysis": analysis,
            "analysis_id": decision_record.id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Decision analysis failed: {str(e)}")


@router.get("/decision/history")
def get_decision_history(user=Depends(firebase_auth_required)):
    """Get decision analysis history"""
    with Session(engine) as session:
        analyses = session.exec(
            select(DecisionAnalysis).where(DecisionAnalysis.user_id == user["uid"])
        ).all()
        
        return {
            "analyses": [
                {
                    "id": a.id,
                    "decision_context": a.decision_context,
                    "blind_spots": json.loads(a.blind_spots or "[]"),
                    "second_order_effects": json.loads(a.second_order_effects or "[]"),
                    "cognitive_biases": json.loads(a.cognitive_biases or "[]"),
                    "recommendation": a.recommendation,
                    "created_at": a.created_at.isoformat()
                }
                for a in analyses
            ]
        }


@router.post("/contradiction/detect")
async def detect_contradictions(body: dict, user=Depends(firebase_auth_required)):
    """Detect contradictions in a set of statements"""
    statements = body.get("statements", [])
    
    if not statements or len(statements) < 2:
        raise HTTPException(status_code=400, detail="At least 2 statements required")
    
    try:
        prompt = f"""Analyze these statements for contradictions:

{chr(10).join(f"{i+1}. {s}" for i, s in enumerate(statements))}

Identify any logical contradictions or inconsistencies. For each contradiction found, specify which statements conflict and explain why.

Respond in JSON format with array of contradictions."""
        
        result = await ai_service.generate(prompt=prompt, mode="think")
        
        try:
            contradictions = json.loads(result.get("output", "[]"))
            if not isinstance(contradictions, list):
                contradictions = []
        except:
            contradictions = []
        
        return {
            "contradictions_found": len(contradictions),
            "contradictions": contradictions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Contradiction detection failed: {str(e)}")


@router.post("/confidence/score")
async def score_confidence(body: dict, user=Depends(firebase_auth_required)):
    """Score confidence level of a statement or claim"""
    statement = body.get("statement")
    context = body.get("context", "")
    
    if not statement:
        raise HTTPException(status_code=400, detail="statement required")
    
    try:
        prompt = f"""Assess the confidence level for this statement.

Statement: {statement}
Context: {context}

Provide:
1. Confidence score (0-1)
2. Reasoning
3. Caveats or uncertainties
4. Suggested verification steps

Respond in JSON format."""
        
        result = await ai_service.generate(prompt=prompt, mode="think")
        
        try:
            analysis = json.loads(result.get("output", "{}"))
        except:
            analysis = {
                "confidence_score": 0.5,
                "reasoning": "Unable to assess",
                "caveats": [],
                "verification_steps": []
            }
        
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Confidence scoring failed: {str(e)}")
