from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Protocol
from uuid import uuid4
lazy from collections.abc import AsyncGenerator, Callable, Coroutine

import jwt
import pytest
from alembic import command
from alembic.config import Config
from asgi_lifespan import LifespanManager
from cryptography.hazmat.primitives.asymmetric import rsa
from fastmcp.utilities.asgi_transport import StreamingASGITransport
from httpx2 import ASGITransport, AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
lazy from pytest_mock import MockerFixture

from app.adapters.configuration.settings import AppSettings, settings
from app.api.dependencies.auth import jwks_client
from app.main import app
lazy from app.adapters.database.models import User


class TokenFactory(Protocol):
    def __call__(
        self,
        scopes: list[str] | None = None,
        expires_at: datetime | None = None,
    ) -> str: ...


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


@pytest.fixture
async def sse_test_client() -> AsyncGenerator[AsyncClient]:
    async with LifespanManager(app) as manager:
        yield AsyncClient(
            transport=StreamingASGITransport(
                manager.app,
                cancel_on_close=False,
            ),
            base_url="http://127.0.0.1:8000",
        )


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


@pytest.fixture(scope="session")
def rsa_private_key() -> rsa.RSAPrivateKey:
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.fixture(autouse=True)
def mock_jwks_client(rsa_private_key: rsa.RSAPrivateKey, mocker: MockerFixture) -> None:
    signing_key = SimpleNamespace(key=rsa_private_key.public_key())
    mocker.patch.object(
        jwks_client,
        "get_signing_key_from_jwt",
        return_value=signing_key,
    )


@pytest.fixture
def make_token(rsa_private_key: rsa.RSAPrivateKey) -> TokenFactory:
    def _make_token(
        scopes: list[str] | None = None,
        expires_at: datetime | None = None,
    ) -> str:
        now = datetime.now(tz=UTC)
        claims: dict[str, Any] = {
            "sub": "test-subject",
            "scp": scopes if scopes is not None else ["users:read", "users:write"],
            "iss": str(settings.auth.issuer),
            "iat": now,
            "exp": (
                expires_at if expires_at is not None else now + timedelta(minutes=5)
            ),
        }
        return jwt.encode(claims, rsa_private_key, algorithm="RS256")

    return _make_token


@pytest.fixture
def auth_headers(make_token: TokenFactory) -> dict[str, str]:
    token = make_token()
    return {"Authorization": f"Bearer {token}"}
