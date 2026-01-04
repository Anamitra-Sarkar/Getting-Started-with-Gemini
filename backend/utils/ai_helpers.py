"""Helper utilities for working with AI service responses"""
from fastapi import HTTPException
from typing import Dict, Any


def check_ai_response(result: Dict[str, Any], operation: str = "AI operation") -> Dict[str, Any]:
    """
    Check if an AI service response contains an error and raise appropriate HTTPException.
    
    Args:
        result: Response dict from ai_service.generate()
        operation: Name of the operation being performed (for error messages)
    
    Returns:
        The result dict if no error was detected
        
    Raises:
        HTTPException: If the AI service returned an error
    """
    if result.get("status") == "error":
        error_msg = result.get("output", "AI service unavailable")
        detail = f"{operation} failed: {error_msg}"
        raise HTTPException(status_code=503, detail=detail)
    return result
