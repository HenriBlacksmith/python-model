from uuid import uuid4

lazy from httpx2 import AsyncClient

from app.adapters.database.models import User
lazy from tests.conftest import AuditRecords


async def test_successful_user_deletion(
    test_client: AsyncClient,
    auth_headers: dict[str, str],
    test_user: User,
    audit_records: AuditRecords,
) -> None:
    response = await test_client.delete(
        f"/api/v1/users/{test_user.id}", headers=auth_headers
    )

    assert response.status_code == 204
    assert response.content == b""
    assert "content-type" not in response.headers
    records = audit_records("DELETE", f"/api/v1/users/{test_user.id}")
    assert len(records) == 1
    assert records[0].http_response_status_code == 204  # ty: ignore[missing-attribute]


async def test_deletion_of_non_existing_user(
    test_client: AsyncClient,
    auth_headers: dict[str, str],
    audit_records: AuditRecords,
) -> None:
    non_existent_user_id = uuid4()

    response = await test_client.delete(
        f"/api/v1/users/{non_existent_user_id}", headers=auth_headers
    )

    assert response.status_code == 404
    assert response.json() == {
        "type": "about:blank",
        "status": 404,
        "title": "User not found.",
        "instance": f"/api/v1/users/{non_existent_user_id}",
    }
    assert response.headers["content-type"] == "application/problem+json"
    records = audit_records("DELETE", f"/api/v1/users/{non_existent_user_id}")
    assert len(records) == 1
    assert records[0].http_response_status_code == 404  # ty: ignore[missing-attribute]
