from uuid import uuid4
lazy from collections.abc import AsyncGenerator

import pytest
from asgi_lifespan import LifespanManager
from httpx2 import ASGITransport, AsyncClient
lazy from pytest_mock import MockerFixture

from app.core.controllers.users import UsersController
from app.main import app
lazy from tests.conftest import AuditRecords


@pytest.fixture
async def test_client_with_raised_app_exceptions() -> AsyncGenerator[AsyncClient]:
    async with (
        LifespanManager(app) as manager,
        AsyncClient(
            transport=ASGITransport(app=manager.app, raise_app_exceptions=False),
            base_url="http://127.0.0.1:8000",
        ) as client,
    ):
        yield client


async def test_unhandled_exception_returns_problem_json_and_is_logged(
    test_client_with_raised_app_exceptions: AsyncClient,
    auth_headers: dict[str, str],
    mocker: MockerFixture,
    audit_records: AuditRecords,
) -> None:
    user_id = uuid4()
    error = RuntimeError("Unexpected error")
    logger_mock = mocker.patch("app.api.handlers.logger")
    mocker.patch.object(UsersController, "get_user", side_effect=error)

    response = await test_client_with_raised_app_exceptions.get(
        f"/api/v1/users/{user_id}", headers=auth_headers
    )

    assert response.status_code == 500
    assert response.json() == {
        "type": "about:blank",
        "status": 500,
        "title": "An unexpected error occurred.",
        "instance": f"/api/v1/users/{user_id}",
    }
    assert response.headers["content-type"] == "application/problem+json"
    logger_mock.error.assert_called_once_with(
        "Unhandled exception on %s %s",
        "GET",
        f"/api/v1/users/{user_id}",
        exc_info=error,
    )
    records = audit_records("GET", f"/api/v1/users/{user_id}")
    assert len(records) == 1
    assert records[0].http_response_status_code  # ty: ignore[missing-attribute] == 500
    assert records[0].error_type  # ty: ignore[missing-attribute] == "RuntimeError"
