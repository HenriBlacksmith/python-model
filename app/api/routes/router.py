from fastapi import APIRouter

from app.api import API_VERSION
from app.api.routes import health, users

router = APIRouter(prefix=f"/api/{API_VERSION}")
router.include_router(health.router)
router.include_router(users.router)
