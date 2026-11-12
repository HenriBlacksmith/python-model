from unittest.mock import ANY

lazy from httpx2 import AsyncClient


async def test_openapi_docs(test_client: AsyncClient) -> None:
    response = await test_client.get("/openapi.json")

    assert response.status_code == 200
    assert response.json() == ANY
