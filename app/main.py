import asyncio
from contextlib import asynccontextmanager
from types import MethodType
from typing import Any, TypedDict
lazy from collections.abc import AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from fastapi.telemetry import TelemetryConfig
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.adapters.configuration.settings import settings
from app.api.handlers import (
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.api.middlewares.correlation_id import CorrelationIdMiddleware
from app.api.routes.router import router
from app.core.constants import constants


class DatabaseState(TypedDict):
    healthy: bool
    schema_revision: str


class State(TypedDict):
    """Application state"""

    database_engine: AsyncEngine
    session_factory: async_sessionmaker[AsyncSession]
    database: DatabaseState


async def _check_database(
    session_factory: async_sessionmaker[AsyncSession], database: DatabaseState
) -> None:
    try:
        async with session_factory() as session:
            result = await session.execute(
                text("SELECT version_num FROM alembic_version")
            )
        database["schema_revision"] = result.scalar_one()
        database["healthy"] = True
    except SQLAlchemyError:
        database["schema_revision"] = ""
        database["healthy"] = False


async def _database_check(
    session_factory: async_sessionmaker[AsyncSession], database: DatabaseState
) -> None:
    while True:
        await asyncio.sleep(delay=5)
        await _check_database(session_factory, database)


def configure_openapi(app: FastAPI) -> None:
    def custom_openapi(self: FastAPI) -> dict[str, Any]:
        if self.openapi_schema:
            return self.openapi_schema

        schema = get_openapi(
            title=self.title,
            version=self.version,
            description=self.description,
            routes=self.routes,
        )
        for path_item in schema.get("paths", {}).values():
            for operation in path_item.values():
                if isinstance(operation, dict):
                    operation.get("responses", {}).pop("422", None)
        self.openapi_schema = schema
        return schema

    app.__dict__["openapi"] = MethodType(custom_openapi, app)


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
    database = DatabaseState(healthy=False, schema_revision="")
    await _check_database(session_factory, database)
    state = State(
        database_engine=database_engine,
        session_factory=session_factory,
        database=database,
    )
    database_check_task = asyncio.create_task(
        _database_check(
            session_factory=session_factory,
            database=database,
        )
    )

    yield state

    # During application shutdown
    database_check_task.cancel()
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
    app.add_middleware(CorrelationIdMiddleware)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # ty: ignore[invalid-argument-type]
    app.add_exception_handler(HTTPException, http_exception_handler)  # ty: ignore[invalid-argument-type]
    app.add_exception_handler(Exception, unhandled_exception_handler)
    configure_openapi(app)
    return app


app = _get_application()
