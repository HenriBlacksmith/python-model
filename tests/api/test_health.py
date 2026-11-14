import pytest
lazy from httpx2 import AsyncClient


@pytest.mark.parametrize(
    "query",
    [
        "",
        "?check_type=liveness",
    ],
)
async def test_liveness_check(
    test_client: AsyncClient, release_id: str, query: str
) -> None:
    response = await test_client.get(f"/api/v1/health{query}")

    assert response.status_code == 200
    assert response.json() == {
        "status": "pass",
        "version": "v1",
        "releaseId": release_id,
    }


async def test_readiness_check(test_client: AsyncClient, release_id: str) -> None:
    response = await test_client.get("/api/v1/health?check_type=readiness")

    assert response.status_code == 200
    assert response.json() == {
        "status": "pass",
        "version": "v1",
        "releaseId": release_id,
        "notes": [
            "datastoreSchemaVersion=1e7be203686b",
        ],
        "checks": {
            "datastore:health": {"componentType": "datastore", "status": "pass"}
        },
    }
