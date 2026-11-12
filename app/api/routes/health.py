from fastapi import APIRouter

from app.api import API_VERSION, Tags
from app.api.models.health import HealthCheckResponse, HealthStatus
from app.core.constants import constants

router = APIRouter(tags=[Tags.Health])


@router.get("/health")
async def health_check() -> HealthCheckResponse:
    """
    Health check endpoint to verify that the API is running.
    """
    return HealthCheckResponse(
        status=HealthStatus.PASS,
        version=API_VERSION,
        release_id=constants.version,
    )
