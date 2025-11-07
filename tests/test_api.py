import os
from fastapi.testclient import TestClient

os.environ["DEMO_MODE"] = "1"

from api.ask import app  # import after setting env var


def test_api_demo_mode_basic():
    client = TestClient(app)
    payload = {"prompt": "Explain gravity in simple terms"}
    resp = client.post("/", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    # demo mode returns a 'result' key with demo text
    assert isinstance(data, dict)
    assert "result" in data
    assert "Demo" in data["result"] or "explanation" or "explain" or "explain" in data["result"].lower()
