from typing import Annotated

from fastapi import APIRouter, Query, Request

from app.api import API_VERSION, Tags
from app.api.models.health import Check, CheckType, HealthCheckResponse, HealthStatus
from app.core.constants import constants

router = APIRouter(tags=[Tags.Health])


@router.get(
    "/health",
    response_model_exclude_none=True,
)
async def health_check(
    request: Request,
    check_type: Annotated[CheckType, Query()] = CheckType.LIVENESS,
) -> HealthCheckResponse:
    """
    Health check endpoint to verify that the API is running.
    """
    if check_type == CheckType.LIVENESS:
        return HealthCheckResponse(
            status=HealthStatus.PASS,
            version=API_VERSION,
            release_id=constants.version,
            notes=None,
            checks=None,
        )
    return HealthCheckResponse(
        status=HealthStatus.PASS,
        version=API_VERSION,
        release_id=constants.version,
        notes=[f"datastoreSchemaVersion={request.state['database']['schema_revision']}"]
        if request.state["database"]["healthy"]
        else None,
        checks={
            "datastore:health": Check(
                component_type="datastore",
                status=HealthStatus.PASS
                if request.state["database"]["healthy"]
                else HealthStatus.FAIL,
            )
        },
    )
