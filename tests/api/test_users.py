from unittest.mock import ANY
from uuid import uuid4

lazy from httpx2 import AsyncClient

lazy from app.adapters.database.models import User


async def test_successful_user_creation(test_client: AsyncClient) -> None:
    response = await test_client.post(
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


async def test_user_creation_with_invalid_username(test_client: AsyncClient) -> None:
    response = await test_client.post(
        "/api/v1/users",
        json={
            "username": "",
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "status": 400,
        "title": "The request was invalid.",
        "type": "about:blank",
        "detail": "",
        "instance": "/api/v1/users",
    }
    assert response.headers["content-type"] == "application/problem+json"


async def test_successful_user_retrieval(
    test_client: AsyncClient, test_user: User
) -> None:
    response = await test_client.get(f"/api/v1/users/{test_user.id}")

    assert response.status_code == 200
    assert response.json() == {
        "username": test_user.name,
        "userId": str(test_user.id),
        "createdAt": ANY,
        "updatedAt": ANY,
    }


async def test_retrieval_of_non_existent_user(test_client: AsyncClient) -> None:
    random_id = uuid4()
    response = await test_client.get(f"/api/v1/users/{random_id}")

    assert response.status_code == 404
    assert response.json() == {
        "status": 404,
        "title": "User not found.",
        "type": "about:blank",
    }
    assert response.headers["content-type"] == "application/problem+json"


async def test_successful_user_update(
    test_client: AsyncClient, test_user: User
) -> None:
    response = await test_client.put(
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


async def test_successful_user_deletion(
    test_client: AsyncClient, test_user: User
) -> None:
    response = await test_client.delete(f"/api/v1/users/{test_user.id}")

    assert response.status_code == 204
    assert response.content == b""
