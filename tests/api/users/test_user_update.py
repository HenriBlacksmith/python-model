from unittest.mock import ANY
from uuid import uuid4

lazy from httpx2 import AsyncClient

from app.adapters.database.models import User


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
    assert response.headers["content-type"] == "application/json"


async def test_update_of_non_existing_user(test_client: AsyncClient) -> None:
    non_existent_user_id = uuid4()

    response = await test_client.put(
        f"/api/v1/users/{non_existent_user_id}",
        json={
            "username": "updateduser",
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "type": "about:blank",
        "status": 404,
        "title": "User not found.",
        "instance": f"/api/v1/users/{non_existent_user_id}",
    }
    assert response.headers["content-type"] == "application/problem+json"
