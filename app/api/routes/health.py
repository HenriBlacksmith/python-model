from fastapi import APIRouter

from app.api import API_VERSION
from app.api.models.health import HealthCheckResponse, HealthStatus
from app.core.constants import constants

router = APIRouter()


@router.get("/health", tags=["Health"])
async def health_check() -> HealthCheckResponse:
    """
    Health check endpoint to verify that the API is running.
    """
    return HealthCheckResponse(
        status=HealthStatus.PASS,
        version=API_VERSION,
        release_id=constants.version,
    )
