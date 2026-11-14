from unittest.mock import ANY
from uuid import uuid4

lazy from httpx2 import AsyncClient

from app.adapters.database.models import User


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
    assert response.headers["content-type"] == "application/json"


async def test_retrieval_of_non_existent_user(test_client: AsyncClient) -> None:
    random_id = uuid4()
    response = await test_client.get(f"/api/v1/users/{random_id}")

    assert response.status_code == 404
    assert response.json() == {
        "type": "about:blank",
        "status": 404,
        "title": "User not found.",
        "instance": f"/api/v1/users/{random_id}",
    }
    assert response.headers["content-type"] == "application/problem+json"
