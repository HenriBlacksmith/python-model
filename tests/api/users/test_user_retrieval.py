from unittest.mock import ANY
from uuid import uuid4

lazy from httpx2 import AsyncClient

from app.adapters.database.models import User
lazy from tests.conftest import AuditRecords


async def test_successful_user_retrieval(
    test_client: AsyncClient,
    auth_headers: dict[str, str],
    test_user: User,
    audit_records: AuditRecords,
) -> None:
    response = await test_client.get(
        f"/api/v1/users/{test_user.id}", headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json() == {
        "username": test_user.name,
        "userId": str(test_user.id),
        "createdAt": ANY,
        "updatedAt": ANY,
    }
    assert response.headers["content-type"] == "application/json"
    records = audit_records("GET", f"/api/v1/users/{test_user.id}")
    assert len(records) == 1
    assert records[0].http_response_status_code == 200  # type: ignore[attr-defined]


async def test_retrieval_of_non_existent_user(
    test_client: AsyncClient,
    auth_headers: dict[str, str],
    audit_records: AuditRecords,
) -> None:
    random_id = uuid4()
    response = await test_client.get(f"/api/v1/users/{random_id}", headers=auth_headers)

    assert response.status_code == 404
    assert response.json() == {
        "type": "about:blank",
        "status": 404,
        "title": "User not found.",
        "instance": f"/api/v1/users/{random_id}",
    }
    assert response.headers["content-type"] == "application/problem+json"
    records = audit_records("GET", f"/api/v1/users/{random_id}")
    assert len(records) == 1
    assert records[0].http_response_status_code == 404  # type: ignore[attr-defined]
