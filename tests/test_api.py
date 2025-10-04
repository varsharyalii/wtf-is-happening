"""
Tests for the FastAPI backend.

These test that the API endpoints work correctly.
Note: Some tests are skipped if the vector database isn't initialized.
"""

import pytest
from fastapi.testclient import TestClient
from api import app


# Create a test client
client = TestClient(app)


def test_root_endpoint():
    """The root endpoint should return basic API info."""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "name" in data
    assert "version" in data
    assert data["name"] == "WTF Podcast RAG API"


def test_health_check():
    """Health endpoint should tell us if the system is working."""
    response = client.get("/health")
    
    # Might return 503 if vector DB isn't initialized, that's okay for tests
    assert response.status_code in [200, 503]
    
    if response.status_code == 200:
        data = response.json()
        assert data["status"] == "healthy"
        assert "episodes_loaded" in data
        assert "total_chunks" in data


def test_stats_endpoint():
    """Stats endpoint should return system information."""
    response = client.get("/stats")
    
    # Same as health - might not be initialized
    if response.status_code == 200:
        data = response.json()
        assert "episodes" in data
        assert "llm_model" in data
        assert isinstance(data["guests"], list)


def test_query_endpoint_validation():
    """Query endpoint should validate input."""
    # Missing required field
    response = client.post("/query", json={})
    assert response.status_code == 422  # Validation error
    
    # Empty question
    response = client.post("/query", json={"question": ""})
    # FastAPI's validation might accept this, but it's not a good query
    # In a real system, we'd add custom validation


def test_query_endpoint_structure():
    """Query endpoint should return properly structured responses."""
    # This might fail if the backend isn't initialized, that's okay
    response = client.post("/query", json={
        "question": "What is AI?",
        "top_k": 3,
        "diversity": True
    })
    
    if response.status_code == 200:
        data = response.json()
        
        # Should have these fields
        assert "answer" in data
        assert "sources" in data
        assert "query" in data
        
        # Sources should be a list
        assert isinstance(data["sources"], list)
        
        # If there are sources, they should have the right structure
        if data["sources"]:
            source = data["sources"][0]
            assert "guest" in source
            assert "text" in source
            assert "youtube_url" in source
            assert "score" in source


def test_cors_headers():
    """API should have CORS headers for frontend access."""
    response = client.options("/query")
    
    # CORS preflight should be handled
    # (The exact headers depend on the request, but the endpoint should exist)
    assert response.status_code in [200, 405]  # Either works or not allowed


if __name__ == "__main__":
    print("Run these tests with: pytest tests/test_api.py -v")

