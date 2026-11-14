from typing import Annotated

from fastapi import APIRouter, Query, Request, Response, status

from app.api import API_VERSION, Tags
from app.api.models.health import (
    Check,
    CheckType,
    HealthCheckResponse,
    HealthJSONResponse,
    HealthStatus,
)
from app.core.constants import constants

router = APIRouter(tags=[Tags.Health])


@router.get(
    "/health",
    response_class=HealthJSONResponse,
    response_model_exclude_none=True,
)
async def health_check(
    request: Request,
    response: Response,
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
    datastore_health_status = HealthStatus.FAIL
    notes = None
    response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    if request.state["database"]["healthy"]:
        response.status_code = status.HTTP_200_OK
        datastore_health_status = HealthStatus.PASS
        notes = [
            f"datastoreSchemaVersion={request.state['database']['schema_revision']}"
        ]
    return HealthCheckResponse(
        status=HealthStatus.PASS,
        version=API_VERSION,
        release_id=constants.version,
        notes=notes,
        checks={
            "datastore:health": Check(
                component_type="datastore",
                status=datastore_health_status,
            )
        },
    )
