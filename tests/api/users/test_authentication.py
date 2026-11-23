from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

import pytest
lazy from httpx2 import AsyncClient

lazy from tests.conftest import AuditRecords, TokenFactory

READ_SCOPE = "users:read"
WRITE_SCOPE = "users:write"

ROUTES: list[tuple[str, str, bool]] = [
    ("post", "/api/v1/users", True),
    ("get", "/api/v1/users", False),
    ("get", f"/api/v1/users/{uuid4()}", False),
    ("put", f"/api/v1/users/{uuid4()}", True),
    ("delete", f"/api/v1/users/{uuid4()}", False),
]

PROTECTED_ROUTES: list[tuple[str, str, bool, str]] = [
    ("post", "/api/v1/users", True, WRITE_SCOPE),
    ("get", "/api/v1/users", False, READ_SCOPE),
    ("get", f"/api/v1/users/{uuid4()}", False, READ_SCOPE),
    ("put", f"/api/v1/users/{uuid4()}", True, WRITE_SCOPE),
    ("delete", f"/api/v1/users/{uuid4()}", False, WRITE_SCOPE),
]


def _request_kwargs(has_body: bool) -> dict[str, Any]:
    return {"json": {"username": "authuser"}} if has_body else {}


def _assert_audited(
    audit_records: AuditRecords, method: str, url: str, expected_status: int
) -> None:
    records = audit_records(method, url)
    assert len(records) == 1
    assert records[0].http_response_status_code == expected_status  # type: ignore[attr-defined]
    assert records[0].client_address  # type: ignore[attr-defined]


@pytest.mark.parametrize(("method", "url", "has_body"), ROUTES)
async def test_missing_token_returns_401(
    test_client: AsyncClient,
    method: str,
    url: str,
    has_body: bool,
    audit_records: AuditRecords,
) -> None:
    response = await getattr(test_client, method)(url, **_request_kwargs(has_body))

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
    assert response.json() == {
        "type": "about:blank",
        "status": 401,
        "title": "Missing authentication token.",
        "instance": url,
    }
    assert response.headers["content-type"] == "application/problem+json"
    _assert_audited(audit_records, method, url, 401)


@pytest.mark.parametrize(("method", "url", "has_body"), ROUTES)
async def test_malformed_token_returns_401(
    test_client: AsyncClient,
    method: str,
    url: str,
    has_body: bool,
    audit_records: AuditRecords,
) -> None:
    response = await getattr(test_client, method)(
        url,
        headers={"Authorization": "Bearer not-a-jwt"},
        **_request_kwargs(has_body),
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
    assert response.json() == {
        "type": "about:blank",
        "status": 401,
        "title": "Invalid authentication token.",
        "instance": url,
    }
    assert response.headers["content-type"] == "application/problem+json"
    _assert_audited(audit_records, method, url, 401)


@pytest.mark.parametrize(("method", "url", "has_body"), ROUTES)
async def test_expired_token_returns_401(
    test_client: AsyncClient,
    make_token: TokenFactory,
    method: str,
    url: str,
    has_body: bool,
    audit_records: AuditRecords,
) -> None:
    token = make_token(expires_at=datetime.now(tz=UTC) - timedelta(minutes=1))
    response = await getattr(test_client, method)(
        url,
        headers={"Authorization": f"Bearer {token}"},
        **_request_kwargs(has_body),
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
    assert response.json() == {
        "type": "about:blank",
        "status": 401,
        "title": "Invalid authentication token.",
        "instance": url,
    }
    assert response.headers["content-type"] == "application/problem+json"
    _assert_audited(audit_records, method, url, 401)


@pytest.mark.parametrize(
    ("method", "url", "has_body", "required_scope"), PROTECTED_ROUTES
)
async def test_insufficient_scopes_return_403(
    test_client: AsyncClient,
    make_token: TokenFactory,
    method: str,
    url: str,
    has_body: bool,
    required_scope: str,
    audit_records: AuditRecords,
) -> None:
    other_scope = READ_SCOPE if required_scope == WRITE_SCOPE else WRITE_SCOPE
    headers = {"Authorization": f"Bearer {make_token(scopes=[other_scope])}"}
    response = await getattr(test_client, method)(
        url,
        headers=headers,
        **_request_kwargs(has_body),
    )

    assert response.status_code == 403
    assert response.json() == {
        "type": "about:blank",
        "status": 403,
        "title": "Insufficient scopes.",
        "instance": url,
    }
    assert response.headers["content-type"] == "application/problem+json"
    _assert_audited(audit_records, method, url, 403)


@pytest.mark.parametrize(("method", "url", "has_body"), ROUTES)
async def test_wrong_audience_returns_401(
    test_client: AsyncClient,
    make_token: TokenFactory,
    method: str,
    url: str,
    has_body: bool,
    audit_records: AuditRecords,
) -> None:
    token = make_token(audience="other-client")
    response = await getattr(test_client, method)(
        url,
        headers={"Authorization": f"Bearer {token}"},
        **_request_kwargs(has_body),
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
    assert response.json() == {
        "type": "about:blank",
        "status": 401,
        "title": "Invalid authentication token.",
        "instance": url,
    }
    assert response.headers["content-type"] == "application/problem+json"
    _assert_audited(audit_records, method, url, 401)


async def test_valid_token_grants_access(
    test_client: AsyncClient,
    make_token: TokenFactory,
    audit_records: AuditRecords,
) -> None:
    headers = {"Authorization": f"Bearer {make_token()}"}
    response = await test_client.post(
        "/api/v1/users",
        headers=headers,
        json={
            "username": "authuser",
        },
    )

    assert response.status_code == 201
    _assert_audited(audit_records, "post", "/api/v1/users", 201)
    records = audit_records("POST", "/api/v1/users")
    assert records[0].user_id == "test-subject"  # type: ignore[attr-defined]
