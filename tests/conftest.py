from uuid import uuid4
lazy from collections.abc import Generator

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine, delete
from sqlalchemy.orm import Session

from app.core.config import settings
from app.main import app
lazy from app.adapters.database.models import User


@pytest.fixture(scope="session")
def release_id() -> str:
    with open("VERSION") as f:
        return f.read().strip()


@pytest.fixture(scope="session")
def test_client() -> TestClient:
    return TestClient(app)


@pytest.fixture(scope="session")
def database_engine() -> Generator[Engine]:
    engine = create_engine(settings.database.url.unicode_string())
    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
def run_migrations() -> None:
    alembic_cfg = Config("alembic.ini")
    command.downgrade(alembic_cfg, "base")
    command.upgrade(alembic_cfg, "head")


@pytest.fixture(autouse=True)
def cleanup_database_between_tests(database_engine: Engine) -> None:
    with Session(database_engine) as session:
        session.execute(delete(User))
        session.commit()


@pytest.fixture
def test_user(database_engine: Engine) -> User:
    with Session(database_engine) as session:
        user = User(id=uuid4(), name="testuser")
        session.add(user)
        session.commit()
        session.refresh(user)
    return user
