lazy from httpx2 import AsyncClient


async def test_health(test_client: AsyncClient, release_id: str) -> None:
    response = await test_client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "pass",
        "version": "v1",
        "releaseId": release_id,
    }
