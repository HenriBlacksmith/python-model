from enum import StrEnum

from app.api.models import APIModel


class CheckType(StrEnum):
    READINESS = "readiness"
    LIVENESS = "liveness"


class HealthStatus(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"


class Check(APIModel):
    component_type: str
    status: HealthStatus


class HealthCheckResponse(APIModel):
    status: HealthStatus
    version: str
    release_id: str
    checks: dict[str, Check] | None
    notes: list[str] | None
