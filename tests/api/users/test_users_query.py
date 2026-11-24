from unittest.mock import ANY
lazy from collections.abc import Callable, Coroutine

import pytest
lazy from httpx2 import AsyncClient

lazy from app.adapters.database.models import User
lazy from tests.conftest import AuditRecords


@pytest.mark.parametrize(
    "query",
    [
        "page=1&page_size=10",
        "page=1",
    ],
)
async def test_successful_user_list_no_user(
    test_client: AsyncClient,
    auth_headers: dict[str, str],
    query: str,
    audit_records: AuditRecords,
) -> None:
    response = await test_client.get(f"/api/v1/users?{query}", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == {
        "pageSize": 10,
        "page": 1,
        "total": 0,
        "data": [],
        "links": {
            "self": "http://blacksmith.local/api/v1/users?page=1&page_size=10",
            "first": "http://blacksmith.local/api/v1/users?page=1&page_size=10",
            "last": "http://blacksmith.local/api/v1/users?page=1&page_size=10",
            "prev": None,
            "next": None,
        },
    }
    assert response.headers["content-type"] == "application/json"
    records = audit_records("GET", "/api/v1/users")
    assert len(records) == 1
    assert records[0].http_response_status_code  # ty: ignore[missing-attribute] == 200


@pytest.mark.parametrize(
    "query",
    [
        "page=1&page_size=10",
        "page=1",
    ],
)
async def test_successful_user_list_multiple_users_one_page(
    test_client: AsyncClient,
    auth_headers: dict[str, str],
    query: str,
    create_test_users: Callable[[list[str]], Coroutine[None, None, list[User]]],
    audit_records: AuditRecords,
) -> None:
    await create_test_users(["amy", "bob", "carl", "dave", "eddie", "fiona", "gayle"])

    response = await test_client.get(f"/api/v1/users?{query}", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == {
        "pageSize": 10,
        "page": 1,
        "total": 7,
        "data": [
            {
                "username": "amy",
                "userId": ANY,
                "createdAt": ANY,
                "updatedAt": ANY,
            },
            {
                "username": "bob",
                "userId": ANY,
                "createdAt": ANY,
                "updatedAt": ANY,
            },
            {
                "username": "carl",
                "userId": ANY,
                "createdAt": ANY,
                "updatedAt": ANY,
            },
            {
                "username": "dave",
                "userId": ANY,
                "createdAt": ANY,
                "updatedAt": ANY,
            },
            {
                "username": "eddie",
                "userId": ANY,
                "createdAt": ANY,
                "updatedAt": ANY,
            },
            {
                "username": "fiona",
                "userId": ANY,
                "createdAt": ANY,
                "updatedAt": ANY,
            },
            {
                "username": "gayle",
                "userId": ANY,
                "createdAt": ANY,
                "updatedAt": ANY,
            },
        ],
        "links": {
            "self": "http://blacksmith.local/api/v1/users?page=1&page_size=10",
            "first": "http://blacksmith.local/api/v1/users?page=1&page_size=10",
            "last": "http://blacksmith.local/api/v1/users?page=1&page_size=10",
            "prev": None,
            "next": None,
        },
    }
    assert response.headers["content-type"] == "application/json"
    records = audit_records("GET", "/api/v1/users")
    assert len(records) == 1
    assert records[0].http_response_status_code  # ty: ignore[missing-attribute] == 200


async def test_successful_user_list_multiple_users_two_pages(
    test_client: AsyncClient,
    auth_headers: dict[str, str],
    create_test_users: Callable[[list[str]], Coroutine[None, None, list[User]]],
    audit_records: AuditRecords,
) -> None:
    await create_test_users(["amy", "bob", "carl", "dave", "eddie", "fiona", "gayle"])

    response = await test_client.get(
        "/api/v1/users?page=1&page_size=5", headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json() == {
        "pageSize": 5,
        "page": 1,
        "total": 7,
        "data": [
            {
                "username": "amy",
                "userId": ANY,
                "createdAt": ANY,
                "updatedAt": ANY,
            },
            {
                "username": "bob",
                "userId": ANY,
                "createdAt": ANY,
                "updatedAt": ANY,
            },
            {
                "username": "carl",
                "userId": ANY,
                "createdAt": ANY,
                "updatedAt": ANY,
            },
            {
                "username": "dave",
                "userId": ANY,
                "createdAt": ANY,
                "updatedAt": ANY,
            },
            {
                "username": "eddie",
                "userId": ANY,
                "createdAt": ANY,
                "updatedAt": ANY,
            },
        ],
        "links": {
            "self": "http://blacksmith.local/api/v1/users?page=1&page_size=5",
            "first": "http://blacksmith.local/api/v1/users?page=1&page_size=5",
            "last": "http://blacksmith.local/api/v1/users?page=2&page_size=5",
            "prev": None,
            "next": "http://blacksmith.local/api/v1/users?page=2&page_size=5",
        },
    }
    assert response.headers["content-type"] == "application/json"

    response = await test_client.get(
        "/api/v1/users?page=2&page_size=5", headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json() == {
        "pageSize": 5,
        "page": 2,
        "total": 7,
        "data": [
            {
                "username": "fiona",
                "userId": ANY,
                "createdAt": ANY,
                "updatedAt": ANY,
            },
            {
                "username": "gayle",
                "userId": ANY,
                "createdAt": ANY,
                "updatedAt": ANY,
            },
        ],
        "links": {
            "self": "http://blacksmith.local/api/v1/users?page=2&page_size=5",
            "first": "http://blacksmith.local/api/v1/users?page=1&page_size=5",
            "last": "http://blacksmith.local/api/v1/users?page=2&page_size=5",
            "prev": "http://blacksmith.local/api/v1/users?page=1&page_size=5",
            "next": None,
        },
    }
    assert response.headers["content-type"] == "application/json"
    records = audit_records("GET", "/api/v1/users")
    assert len(records) == 2
    assert records[0].http_response_status_code  # ty: ignore[missing-attribute] == 200
    assert records[1].http_response_status_code  # ty: ignore[missing-attribute] == 200
