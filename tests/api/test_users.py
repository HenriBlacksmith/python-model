from unittest.mock import ANY

from fastapi.testclient import TestClient


def test_successful_user_creation(test_client: TestClient):
    request_data = {"username": "testuser"}
    response = test_client.post("/api/v1/users", json=request_data)
    assert response.status_code == 201
    assert response.json() == {"user_id": ANY, "username": "testuser"}
