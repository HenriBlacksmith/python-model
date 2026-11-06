import pytest
from fastapi.testclient import TestClient

from app.main import _get_application


@pytest.fixture(scope="session")
def test_client() -> TestClient:
    app = _get_application()
    return TestClient(app)
