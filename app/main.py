from contextlib import asynccontextmanager
from typing import TypedDict
lazy from collections.abc import AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.telemetry import TelemetryConfig
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.api.handlers import http_exception_handler, validation_exception_handler
from app.api.routes.router import router
from app.core.config import settings
from app.core.constants import constants


class State(TypedDict):
    """Application state"""

    database_engine: AsyncEngine
    session_factory: async_sessionmaker[AsyncSession]


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[State]:
    """Application lifespan context manager"""
    # During application startup
    database_engine = create_async_engine(
        settings.database.url.unicode_string(),
        connect_args={},
        pool_pre_ping=True,
        pool_recycle=settings.database.pool_recycle,
        pool_size=settings.database.pool_size,
    )
    session_factory = async_sessionmaker(
        bind=database_engine,
        expire_on_commit=True,
    )
    yield State(
        database_engine=database_engine,
        session_factory=session_factory,
    )

    # During application shutdown
    await database_engine.dispose()


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
    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # ty: ignore[invalid-argument-type]
    app.add_exception_handler(HTTPException, http_exception_handler)  # ty: ignore[invalid-argument-type]
    return app


app = _get_application()
