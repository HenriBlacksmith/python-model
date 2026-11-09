from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import TypedDict

from fastapi import FastAPI
from fastapi.telemetry import TelemetryConfig

from app.api.routes.router import router
from app.core.constants import constants


class State(TypedDict):
    """Application state"""

    ...


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[State]:
    """Application lifespan context manager"""
    state: State = {}
    yield state


def _get_application() -> FastAPI:
    """Application Factory"""
    app = FastAPI(
        lifespan=lifespan,
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
