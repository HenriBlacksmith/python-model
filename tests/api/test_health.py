lazy from collections.abc import AsyncGenerator

import pytest
from asgi_lifespan import LifespanManager
from httpx2 import ASGITransport, AsyncClient
from sqlalchemy.exc import SQLAlchemyError
lazy from pytest_mock import MockerFixture

from app.main import app


@pytest.fixture
async def test_client_with_failing_database(
    mocker: MockerFixture,
) -> AsyncGenerator[AsyncClient]:
    mocker.patch("app.main.AsyncSession.execute", side_effect=SQLAlchemyError)

    async with (
        LifespanManager(app) as manager,
        AsyncClient(
            transport=ASGITransport(app=manager.app),
            base_url="http://127.0.0.1:8000",
        ) as client,
    ):
        yield client


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
    assert response.headers["content-type"] == "application/health+json"


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
    assert response.headers["content-type"] == "application/health+json"


async def test_readiness_check_fails_when_db_fails(
    test_client_with_failing_database: AsyncClient, release_id: str
) -> None:
    response = await test_client_with_failing_database.get(
        "/api/v1/health?check_type=readiness"
    )

    assert response.status_code == 503
    assert response.json() == {
        "status": "pass",
        "version": "v1",
        "releaseId": release_id,
        "checks": {
            "datastore:health": {
                "componentType": "datastore",
                "status": "fail",
            }
        },
    }
    assert response.headers["content-type"] == "application/health+json"
