import logging
from uuid import uuid4
lazy from collections.abc import AsyncGenerator

import pytest
from asgi_lifespan import LifespanManager
from httpx2 import ASGITransport, AsyncClient
lazy from pytest_mock import MockerFixture

from app.core.controllers.users import UsersController
from app.main import app


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
    mocker: MockerFixture,
    caplog: pytest.LogCaptureFixture,
) -> None:
    user_id = uuid4()
    mocker.patch.object(
        UsersController,
        "get_user",
        side_effect=RuntimeError("Unexpected error"),
    )

    with caplog.at_level(logging.ERROR):
        response = await test_client_with_raised_app_exceptions.get(
            f"/api/v1/users/{user_id}"
        )

    assert response.status_code == 500
    assert response.json() == {
        "type": "about:blank",
        "status": 500,
        "title": "An unexpected error occurred.",
        "instance": f"/api/v1/users/{user_id}",
    }
    assert response.headers["content-type"] == "application/problem+json"
    assert "Unhandled exception on GET /api/v1/users/" in caplog.text
    assert "Unexpected error" in caplog.text
    assert any(record.exc_info for record in caplog.records)
