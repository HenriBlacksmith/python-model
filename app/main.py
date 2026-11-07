from fastapi import FastAPI
from fastapi.telemetry import TelemetryConfig

from app.api.routes.router import router
from app.core.constants import constants


def _get_application() -> FastAPI:
    """Application Factory"""
    app = FastAPI(
        title=constants.name,
        telemetry=TelemetryConfig(
            auto_configure=True,
            tracing=True,
            metrics=False,
            logs=True,
        ),
    )
    app.include_router(router=router)
    return app


app = _get_application()
