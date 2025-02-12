import os
from datetime import datetime, timedelta

import jwt
from fastapi.testclient import TestClient

os.environ["JWT_SECRET_KEY"] = "test_secret"
os.environ["CONTAINER_ID"] = "test_container_123"

from main import app

client = TestClient(app)


def create_test_token(user_id="test_user", container_id="test_container_123"):
    secret_key = "test_secret"
    os.environ["JWT_SECRET_KEY"] = secret_key
    os.environ["CONTAINER_ID"] = container_id

    payload = {
        "user_id": user_id,
        "container_id": container_id,
        "exp": datetime.utcnow() + timedelta(days=1),
    }
    return jwt.encode(payload, secret_key, algorithm="HS256")


def test_health_check_with_valid_token():
    token = create_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/health", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"
    assert data["user_id"] == "test_user"


def test_health_check_without_token():
    response = client.get("/health")
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authenticated"


def test_process_data_with_valid_token():
    token = create_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    test_request = {
        "data_type": "sales",
        "processing_level": "advanced",
        "batch_size": 200,
    }

    response = client.post("/api/v1/process", json=test_request, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "initiated"
    assert data["config"]["user_id"] == "test_user"
    assert data["config"]["data_type"] == test_request["data_type"]


def test_process_data_with_invalid_token():
    token = create_test_token(container_id="wrong_container")
    headers = {"Authorization": f"Bearer {token}"}
    test_request = {
        "data_type": "sales",
        "processing_level": "advanced",
        "batch_size": 200,
    }

    response = client.post("/api/v1/process", json=test_request, headers=headers)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid container access"
