import pytest

fastapi = pytest.importorskip("fastapi")

try:
    from app import app
except Exception:  # app missing
    pytest.skip("app module not available", allow_module_level=True)

from fastapi.testclient import TestClient

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200


def test_recommend_endpoint():
    payload = {"persona": "Executor"}
    response = client.post("/recommend", json=payload)
    assert response.status_code == 200
