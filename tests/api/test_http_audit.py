import json
import logging

lazy from collections.abc import AsyncGenerator

import pytest
from asgi_lifespan import LifespanManager
from httpx2 import ASGITransport, AsyncClient

from app.adapters.logging.audit import EcsOtelJsonFormatter, ECS_VERSION
from app.main import app

AUDIT_LOGGER_NAME = "app.audit.http"


@pytest.fixture
async def audit_client() -> AsyncGenerator[AsyncClient]:
    async with (
        LifespanManager(app) as manager,
        AsyncClient(
            transport=ASGITransport(app=manager.app),
            base_url="http://127.0.0.1:8000",
        ) as client,
    ):
        yield client


async def test_http_request_is_audited(
    audit_client: AsyncClient, caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level(level=logging.INFO, logger=AUDIT_LOGGER_NAME):
        response = await audit_client.get("/api/v1/health")

    assert response.status_code == 200
    records = [
        record
        for record in caplog.records
        if record.name == AUDIT_LOGGER_NAME
        and record.url_path == "/api/v1/health"  # type: ignore[attr-defined]
    ]
    assert len(records) == 1
    record = records[0]
    assert record.http_request_method == "GET"  # type: ignore[attr-defined]
    assert record.http_response_status_code == 200  # type: ignore[attr-defined]
    assert record.duration_ms >= 0  # type: ignore[attr-defined]
    assert record.http_request_id  # type: ignore[attr-defined]
    assert record.client_address  # type: ignore[attr-defined]


async def test_http_audit_includes_query_string(
    audit_client: AsyncClient, caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level(level=logging.INFO, logger=AUDIT_LOGGER_NAME):
        response = await audit_client.get("/api/v1/health?check_type=liveness")

    assert response.status_code == 200
    records = [
        record
        for record in caplog.records
        if record.name == AUDIT_LOGGER_NAME
    ]
    assert len(records) == 1
    assert records[0].url_query == "check_type=liveness"  # type: ignore[attr-defined]


async def test_http_audit_includes_correlation_header(
    audit_client: AsyncClient, caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level(level=logging.INFO, logger=AUDIT_LOGGER_NAME):
        response = await audit_client.get(
            "/api/v1/health",
            headers={"X-Correlation-ID": "test-correlation-id"},
        )

    assert response.status_code == 200
    records = [
        record
        for record in caplog.records
        if record.name == AUDIT_LOGGER_NAME
    ]
    assert len(records) == 1
    assert records[0].http_request_id == "test-correlation-id"  # type: ignore[attr-defined]


def test_ecs_otel_json_formatter(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(level=logging.INFO, logger=AUDIT_LOGGER_NAME):
        logging.getLogger(AUDIT_LOGGER_NAME).info(
            "GET /api/v1/health 200",
            extra={
                "http_request_method": "GET",
                "http_response_status_code": 200,
                "url_path": "/api/v1/health",
                "duration_ms": 12,
            },
        )

    assert caplog.records
    formatted = EcsOtelJsonFormatter().format(record=caplog.records[0])
    payload = json.loads(formatted)

    assert payload["ecs.version"] == ECS_VERSION
    assert payload["log.level"] == "INFO"
    assert payload["message"] == "GET /api/v1/health 200"
    assert payload["@timestamp"].endswith("Z")
    assert payload["http.request.method"] == "GET"
    assert payload["http.response.status_code"] == 200
    assert payload["url.path"] == "/api/v1/health"
    assert payload["event.dataset"] == "python-model.audit.http"
