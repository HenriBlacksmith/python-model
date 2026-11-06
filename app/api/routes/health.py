from fastapi import APIRouter

from app.api.models.health import HealthCheckResponse, HealthStatus

router = APIRouter()


@router.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify that the API is running.
    """
    return HealthCheckResponse(status=HealthStatus.PASS)
