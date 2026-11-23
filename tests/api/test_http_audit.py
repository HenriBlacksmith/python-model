import json
import logging

import pytest

from app.adapters.logging.audit import AUDIT_LOGGER_NAME, ECS_VERSION, EcsOtelJsonFormatter


def test_ecs_otel_json_formatter(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(level=logging.INFO, logger=AUDIT_LOGGER_NAME):
        logging.getLogger(AUDIT_LOGGER_NAME).info(
            "GET /api/v1/users 200",
            extra={
                "http_request_method": "GET",
                "http_response_status_code": 200,
                "url_path": "/api/v1/users",
                "duration_ms": 12,
            },
        )

    assert caplog.records
    formatted = EcsOtelJsonFormatter().format(record=caplog.records[0])
    payload = json.loads(formatted)

    assert payload["ecs.version"] == ECS_VERSION
    assert payload["log.level"] == "INFO"
    assert payload["message"] == "GET /api/v1/users 200"
    assert payload["@timestamp"].endswith("Z")
    assert payload["http.request.method"] == "GET"
    assert payload["http.response.status_code"] == 200
    assert payload["url.path"] == "/api/v1/users"
    assert payload["event.dataset"] == "python-model.audit.http"
