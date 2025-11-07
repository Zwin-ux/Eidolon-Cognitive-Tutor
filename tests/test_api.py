import os
import pytest
from fastapi.testclient import TestClient

os.environ["DEMO_MODE"] = "1"
os.environ["RATE_LIMIT_REQUESTS"] = "100"  # high limit for tests

from api.ask import app  # import after setting env var


@pytest.fixture
def client():
    return TestClient(app)


def test_api_demo_mode_basic(client):
    """Test basic demo mode response."""
    payload = {"prompt": "Explain gravity in simple terms"}
    resp = client.post("/", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "result" in data
    assert data["source"] == "demo"
    assert "Demo" in data["result"] or "explain" in data["result"].lower()


def test_api_demo_mode_code_prompt(client):
    """Test demo mode with code-related prompt."""
    payload = {"prompt": "How to implement quicksort"}
    resp = client.post("/", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "result" in data
    assert "steps" in data["result"].lower() or "implement" in data["result"].lower()


def test_api_session_id_returned(client):
    """Test that session ID is returned."""
    payload = {"prompt": "Test prompt"}
    resp = client.post("/", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "session_id" in data
    assert len(data["session_id"]) > 0


def test_api_session_id_persistence(client):
    """Test that provided session ID is returned."""
    session_id = "test-session-123"
    payload = {"prompt": "Test prompt", "session_id": session_id}
    resp = client.post("/", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["session_id"] == session_id


def test_api_empty_prompt(client):
    """Test API with empty prompt."""
    payload = {"prompt": ""}
    resp = client.post("/", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "result" in data
    assert "Please enter" in data["result"]


def test_api_history_endpoint(client):
    """Test history retrieval endpoint."""
    # First make a request
    session_id = "test-history-session"
    payload = {"prompt": "Test question", "session_id": session_id}
    client.post("/", json=payload)
    
    # Then retrieve history
    resp = client.get(f"/history/{session_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert "history" in data
    assert isinstance(data["history"], list)
