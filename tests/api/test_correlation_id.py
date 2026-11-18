import uuid

lazy from httpx2 import AsyncClient


async def test_echoes_client_correlation_id(test_client: AsyncClient) -> None:
    response = await test_client.get(
        "/api/v1/health",
        headers={"X-Correlation-ID": "client-provided-id"},
    )

    assert response.status_code == 200
    assert response.headers["x-correlation-id"] == "client-provided-id"


async def test_generates_correlation_id_when_missing(test_client: AsyncClient) -> None:
    response = await test_client.get("/api/v1/health")

    assert response.status_code == 200
    correlation_id_value = uuid.UUID(response.headers["x-correlation-id"])
    assert correlation_id_value.version == 4
