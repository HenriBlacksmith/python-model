from unittest.mock import ANY

lazy from fastapi.testclient import TestClient

lazy from app.adapters.database.models import User


def test_successful_user_creation(test_client: TestClient) -> None:
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


def test_successful_user_retrieval(test_client: TestClient, test_user: User) -> None:
    with test_client as client:
        response = client.get(f"/api/v1/users/{test_user.id}")

    assert response.status_code == 200
    assert response.json() == {
        "username": test_user.name,
        "userId": str(test_user.id),
        "createdAt": ANY,
        "updatedAt": ANY,
    }


def test_successful_user_update(test_client: TestClient, test_user: User) -> None:
    with test_client as client:
        response = client.put(
            f"/api/v1/users/{test_user.id}",
            json={
                "username": "updateduser",
            },
        )

    assert response.status_code == 200
    assert response.json() == {
        "username": "updateduser",
        "userId": str(test_user.id),
        "createdAt": ANY,
        "updatedAt": ANY,
    }


def test_successful_user_deletion(test_client: TestClient, test_user: User) -> None:
    with test_client as client:
        response = client.delete(f"/api/v1/users/{test_user.id}")

    assert response.status_code == 204
    assert response.content == b""
