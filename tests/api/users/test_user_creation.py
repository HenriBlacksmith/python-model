from unittest.mock import ANY

import pytest
lazy from httpx2 import AsyncClient

lazy from tests.conftest import AuditRecords


async def test_successful_user_creation(
    test_client: AsyncClient,
    auth_headers: dict[str, str],
    audit_records: AuditRecords,
) -> None:
    response = await test_client.post(
        "/api/v1/users",
        headers=auth_headers,
        json={
            "username": "testuser",
        },
    )

    assert response.status_code == 201
    assert response.json() == {
        "username": "testuser",
        "userId": ANY,
        "createdAt": ANY,
        "updatedAt": ANY,
    }
    assert response.headers["content-type"] == "application/json"
    records = audit_records("POST", "/api/v1/users")
    assert len(records) == 1
    assert getattr(records[0], "http_response_status_code") == 201
    assert getattr(records[0], "user_id") == "test-subject"
    assert getattr(records[0], "client_address")


@pytest.mark.parametrize(
    ("invalid_username", "expected_error_detail"),
    [
        ("", "String should have at least 2 characters"),
        ("A", "String should have at least 2 characters"),
        ("Ac", "String should match pattern '^[a-z][a-z_]*[a-z]$'"),
        ("a" * 101, "String should have at most 100 characters"),
    ],
)
async def test_user_creation_with_invalid_username(
    test_client: AsyncClient,
    auth_headers: dict[str, str],
    invalid_username: str,
    expected_error_detail: str,
    audit_records: AuditRecords,
) -> None:
    response = await test_client.post(
        "/api/v1/users",
        headers=auth_headers,
        json={
            "username": invalid_username,
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "status": 400,
        "title": "The request was invalid.",
        "type": "about:blank",
        "instance": "/api/v1/users",
        "errors": [
            {
                "detail": expected_error_detail,
                "pointer": "#/username",
            },
        ],
    }
    assert response.headers["content-type"] == "application/problem+json"
    records = audit_records("POST", "/api/v1/users")
    assert len(records) == 1
    assert getattr(records[0], "http_response_status_code") == 400


@pytest.mark.usefixtures("test_user")
async def test_user_creation_with_conflicting_username(
    test_client: AsyncClient,
    auth_headers: dict[str, str],
    audit_records: AuditRecords,
) -> None:
    response = await test_client.post(
        "/api/v1/users",
        headers=auth_headers,
        json={
            "username": "testuser",
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        "status": 409,
        "title": "The requested username is already in use.",
        "type": "about:blank",
        "instance": "/api/v1/users",
    }
    assert response.headers["content-type"] == "application/problem+json"
    records = audit_records("POST", "/api/v1/users")
    assert len(records) == 1
    assert getattr(records[0], "http_response_status_code") == 409
