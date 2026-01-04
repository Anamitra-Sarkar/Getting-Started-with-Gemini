"""Test AI service error handling"""
import pytest
from backend.ai.service import AIService


@pytest.mark.asyncio
async def test_ai_service_without_api_key():
    """Test that AI service returns error response when API key is not configured"""
    # Create service without API key
    service = AIService()
    service.key = None
    
    # Call generate
    result = await service.generate(prompt="test prompt", mode="chat")
    
    # Should return error response, not raise exception
    assert result.get("status") == "error"
    assert result.get("error") == "service_unavailable"
    assert "unavailable" in result.get("output", "").lower()


@pytest.mark.asyncio
async def test_ai_service_with_invalid_url():
    """Test that AI service handles connection errors gracefully"""
    service = AIService()
    service.key = "test-key"
    service.url = "http://invalid-url-that-does-not-exist.local"
    
    result = await service.generate(prompt="test prompt", mode="chat")
    
    # Should return error response with appropriate error type
    assert result.get("status") == "error"
    assert result.get("error") in ["service_error", "unknown_error"]
