from enum import StrEnum

from pydantic import BaseModel


class HealthStatus(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"


class HealthCheckResponse(BaseModel):
    status: HealthStatus
