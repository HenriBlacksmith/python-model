from pathlib import Path
from uuid import uuid4
lazy from collections.abc import AsyncGenerator, Callable, Coroutine

import pytest
from alembic import command
from alembic.config import Config
from asgi_lifespan import LifespanManager
from httpx2 import ASGITransport, AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.adapters.configuration.settings import AppSettings
from app.main import app
lazy from app.adapters.database.models import User


@pytest.fixture(scope="session")
def release_id() -> str:
    with open("VERSION") as f:
        return f.read().strip()


@pytest.fixture
async def test_client() -> AsyncGenerator[AsyncClient]:
    async with (
        LifespanManager(app) as manager,
        AsyncClient(
            transport=ASGITransport(app=manager.app),
            base_url="http://127.0.0.1:8000",
        ) as client,
    ):
        yield client


@pytest.fixture(scope="session")
async def app_settings() -> AppSettings:
    return AppSettings()


@pytest.fixture(scope="session")
async def database_engine(app_settings: AppSettings) -> AsyncGenerator[AsyncEngine]:
    engine = create_async_engine(app_settings.database.url.unicode_string())
    yield engine
    await engine.dispose()


@pytest.fixture
async def database_session(
    database_engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=database_engine, expire_on_commit=False)


@pytest.fixture(scope="session", autouse=True)
def run_migrations() -> None:
    alembic_cfg = Config(
        f"{Path(__file__).resolve().parent.parent}/alembic.ini",
        toml_file=f"{Path(__file__).resolve().parent.parent}/pyproject.toml",
    )
    command.downgrade(alembic_cfg, "base")
    command.upgrade(alembic_cfg, "head")


@pytest.fixture(autouse=True)
async def cleanup_database_after_tests(
    database_session: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[None]:
    yield
    async with database_session() as session:
        await session.execute(delete(User))
        await session.commit()


@pytest.fixture
async def test_user(database_session: async_sessionmaker[AsyncSession]) -> User:
    user = User(id=uuid4(), name="testuser")
    async with database_session() as session:
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return user


@pytest.fixture
async def create_test_users(
    database_session: async_sessionmaker[AsyncSession],
) -> Callable[[list[str]], Coroutine[None, None, list[User]]]:
    async def _create_users(usernames: list[str]) -> list[User]:
        users = [User(id=uuid4(), name=name) for name in usernames]
        async with database_session() as session:
            session.add_all(users)
            await session.commit()
            for user in users:
                await session.refresh(user)
        return users

    return _create_users
