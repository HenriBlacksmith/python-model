from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine, delete
from sqlalchemy.orm import Session

from app.adapters.database.models import User
from app.core.config import settings
from app.main import app


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


@pytest.fixture(autouse=True)
def cleanup_database_between_tests(database_engine: Engine):
    with Session(database_engine) as session:
        session.execute(delete(User))
        session.commit()
