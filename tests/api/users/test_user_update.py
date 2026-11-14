from unittest.mock import ANY

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
