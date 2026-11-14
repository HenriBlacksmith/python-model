lazy from httpx2 import AsyncClient

from app.adapters.database.models import User


async def test_successful_user_deletion(
    test_client: AsyncClient, test_user: User
) -> None:
    response = await test_client.delete(f"/api/v1/users/{test_user.id}")

    assert response.status_code == 204
    assert response.content == b""
    assert "content-type" not in response.headers
