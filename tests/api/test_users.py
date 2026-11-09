from unittest.mock import ANY

from fastapi.testclient import TestClient


def test_successful_user_creation(test_client: TestClient):
    with test_client as client:
        response = client.post(
            "/api/v1/users",
            json={
                "username": "testuser",
            },
        )

    assert response.status_code == 201
    assert response.json() == {
        "username": "testuser",
        "userId": ANY,
        "createdAt": ANY,
        "updatedAt": ANY,
    }
