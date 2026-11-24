import json
import logging
from datetime import UTC, datetime

ECS_VERSION = "8.11.0"
AUDIT_LOGGER_NAME = "app.audit.http"


class EcsOtelJsonFormatter(logging.Formatter):
    """Format log records as JSON following the ECS and OTEL conventions.

    Structured audit fields stored as snake_case attributes on the record
    (via `extra={"http_request_method": ...}`) are re-emitted with their
    dotted ECS / OTEL semantic-convention keys, e.g. `http.request.method`.
    """

    STATES: tuple[str, ...] = (
        "http.request.method",
        "http.request.id",
        "http.response.status_code",
        "http.request.body.bytes",
        "http.response.body.bytes",
        "url.full",
        "url.path",
        "url.query",
        "client.address",
        "client.port",
        "user.id",
        "user_agent.original",
        "error.type",
        "error.message",
    )

    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.fromtimestamp(record.created, tz=UTC)
        payload: dict[str, str | int | list[str]] = {
            "@timestamp": timestamp.isoformat(timespec="milliseconds").replace(
                "+00:00", "Z"
            ),
            "log.level": record.levelname,
            "log.logger": record.name,
            "message": record.getMessage(),
            "event.kind": "event",
            "event.category": ["web"],
            "event.dataset": "python-model.audit.http",
            "event.outcome": (
                "failure" if record.levelno >= logging.WARNING else "success"
            ),
            "ecs.version": ECS_VERSION,
        }
        for state in self.STATES:
            attr = state.replace(".", "_")
            value: str | int | None = getattr(record, attr, None)
            if value is not None:
                payload[state] = value
        duration = getattr(record, "duration_ms", None)
        if isinstance(duration, str | int):
            payload["duration_ms"] = duration
        return json.dumps(payload, separators=(",", ":"))


def configure_audit_logging() -> None:
    """Attach the ECS/OTEL JSON formatter to the audit logger.

    Propagation is kept enabled so that records remain visible to
    `caplog` in tests and to the root OTLP handler configured by
    FastAPI's `TelemetryConfig`.
    """
    handler = logging.StreamHandler()
    handler.setFormatter(EcsOtelJsonFormatter())
    logger = logging.getLogger(AUDIT_LOGGER_NAME)
    logger.setLevel(logging.INFO)
    for existing in list(logger.handlers):
        logger.removeHandler(existing)
    logger.addHandler(handler)
