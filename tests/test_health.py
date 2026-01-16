"""Test health endpoint and MongoDB connectivity"""
import pytest
from fastapi.testclient import TestClient
from backend.app import app


def test_health_basic():
    """Test basic health endpoint returns 200"""
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code in [200, 503]  # 200 if all OK, 503 if MongoDB unavailable
    data = r.json()
    assert "status" in data
    assert data["status"] in ["ok", "degraded"]


def test_health_structure():
    """Test health endpoint returns expected structure"""
    client = TestClient(app)
    r = client.get("/health")
    data = r.json()
    
    # Should include SQL DB status
    assert "sql_db" in data
    assert data["sql_db"] == "connected"
    
    # Should include MongoDB status (might be not_configured if MONGODB_URI not set)
    assert "mongo_db" in data
    assert data["mongo_db"] in ["connected", "unreachable", "not_configured", "error"]


@pytest.mark.asyncio
async def test_health_with_mongodb(monkeypatch):
    """Test health check when MongoDB is configured"""
    # Set a test MongoDB URI (will likely fail to connect, but tests the logic)
    monkeypatch.setenv("MONGODB_URI", "mongodb://localhost:27017/test")
    
    # Import after setting env var
    from backend.app import app
    from fastapi.testclient import TestClient
    
    client = TestClient(app)
    r = client.get("/health")
    
    # Should return response (might be 503 if MongoDB unreachable)
    assert r.status_code in [200, 503]
    data = r.json()
    
    # Should have checked MongoDB
    assert "mongo_db" in data
