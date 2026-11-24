from unittest.mock import ANY
from uuid import uuid4
lazy from collections.abc import Callable, Coroutine

import pytest
lazy from httpx2 import AsyncClient

from app.adapters.database.models import User
lazy from tests.conftest import AuditRecords


async def test_successful_user_update(
    test_client: AsyncClient,
    auth_headers: dict[str, str],
    test_user: User,
    audit_records: AuditRecords,
) -> None:
    response = await test_client.put(
        f"/api/v1/users/{test_user.id}",
        headers=auth_headers,
        json={
            "username": "updateduser",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "username": "updateduser",
        "userId": str(test_user.id),
        "createdAt": ANY,
        "updatedAt": ANY,
    }
    assert response.headers["content-type"] == "application/json"
    records = audit_records("PUT", f"/api/v1/users/{test_user.id}")
    assert len(records) == 1
    assert records[0].http_response_status_code == 200  # ty: ignore[missing-attribute]


async def test_user_update_with_conflicting_username(
    test_client: AsyncClient,
    auth_headers: dict[str, str],
    create_test_users: Callable[[list[str]], Coroutine[None, None, list[User]]],
    audit_records: AuditRecords,
) -> None:
    users = await create_test_users(["testuser", "otheruser"])

    response = await test_client.put(
        f"/api/v1/users/{users[1].id}",
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
        "instance": f"/api/v1/users/{users[1].id}",
    }
    assert response.headers["content-type"] == "application/problem+json"
    records = audit_records("PUT", f"/api/v1/users/{users[1].id}")
    assert len(records) == 1
    assert records[0].http_response_status_code == 409  # ty: ignore[missing-attribute]


@pytest.mark.parametrize(
    ("invalid_username", "expected_error_detail"),
    [
        ("", "String should have at least 2 characters"),
        ("A", "String should have at least 2 characters"),
        ("Ac", "String should match pattern '^[a-z][a-z_]*[a-z]$'"),
        ("a" * 101, "String should have at most 100 characters"),
    ],
)
async def test_user_update_with_invalid_username(
    test_client: AsyncClient,
    auth_headers: dict[str, str],
    test_user: User,
    invalid_username: str,
    expected_error_detail: str,
    audit_records: AuditRecords,
) -> None:
    response = await test_client.put(
        f"/api/v1/users/{test_user.id}",
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
        "instance": f"/api/v1/users/{test_user.id}",
        "errors": [
            {
                "detail": expected_error_detail,
                "pointer": "#/username",
            },
        ],
    }
    assert response.headers["content-type"] == "application/problem+json"
    records = audit_records("PUT", f"/api/v1/users/{test_user.id}")
    assert len(records) == 1
    assert records[0].http_response_status_code == 400  # ty: ignore[missing-attribute]


async def test_update_of_non_existing_user(
    test_client: AsyncClient,
    auth_headers: dict[str, str],
    audit_records: AuditRecords,
) -> None:
    non_existent_user_id = uuid4()

    response = await test_client.put(
        f"/api/v1/users/{non_existent_user_id}",
        headers=auth_headers,
        json={
            "username": "updateduser",
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "type": "about:blank",
        "status": 404,
        "title": "User not found.",
        "instance": f"/api/v1/users/{non_existent_user_id}",
    }
    assert response.headers["content-type"] == "application/problem+json"
    records = audit_records("PUT", f"/api/v1/users/{non_existent_user_id}")
    assert len(records) == 1
    assert records[0].http_response_status_code == 404  # ty: ignore[missing-attribute]
