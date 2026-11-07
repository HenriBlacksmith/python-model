from fastapi import APIRouter

from app.api.routes import health, users

router = APIRouter(prefix="/api/v1", tags=["API"])
router.include_router(health.router)
router.include_router(users.router)
