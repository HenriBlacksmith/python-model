from enum import StrEnum

from app.api.models import APIModel


class HealthStatus(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"


class HealthCheckResponse(APIModel):
    status: HealthStatus
    version: str
    release_id: str
