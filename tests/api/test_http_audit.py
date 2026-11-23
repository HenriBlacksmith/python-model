import json
import logging

from app.adapters.logging.audit import (
    AUDIT_LOGGER_NAME,
    ECS_VERSION,
    EcsOtelJsonFormatter,
)


def test_ecs_otel_json_formatter() -> None:
    record = logging.LogRecord(
        name=AUDIT_LOGGER_NAME,
        level=logging.INFO,
        pathname=__file__,
        lineno=17,
        msg="GET /api/v1/users 200",
        args=(),
        exc_info=None,
    )
    record.http_request_method = "GET"
    record.http_response_status_code = 200
    record.url_path = "/api/v1/users"
    record.user_id = "test-subject"
    record.duration_ms = 12

    formatted = EcsOtelJsonFormatter().format(record=record)
    payload = json.loads(formatted)

    assert payload["ecs.version"] == ECS_VERSION
    assert payload["log.level"] == "INFO"
    assert payload["message"] == "GET /api/v1/users 200"
    assert payload["@timestamp"].endswith("Z")
    assert payload["http.request.method"] == "GET"
    assert payload["http.response.status_code"] == 200
    assert payload["url.path"] == "/api/v1/users"
    assert payload["user.id"] == "test-subject"
    assert payload["event.dataset"] == "python-model.audit.http"
