from unittest.mock import ANY
lazy from collections.abc import Callable, Coroutine

import pytest
lazy from httpx2 import AsyncClient

lazy from app.adapters.database.models import User


@pytest.mark.parametrize(
    "query",
    [
        "page=1&page_size=10",
        "page=1",
    ],
)
async def test_successful_user_list_no_user(
    test_client: AsyncClient, query: str
) -> None:
    response = await test_client.get(f"/api/v1/users?{query}")

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


@pytest.mark.parametrize(
    "query",
    [
        "page=1&page_size=10",
        "page=1",
    ],
)
async def test_successful_user_list_multiple_users_one_page(
    test_client: AsyncClient,
    query: str,
    create_test_users: Callable[[list[str]], Coroutine[None, None, list[User]]],
) -> None:
    await create_test_users(["amy", "bob", "carl", "dave", "eddie", "fiona", "gayle"])

    response = await test_client.get(f"/api/v1/users?{query}")

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


async def test_successful_user_list_multiple_users_two_pages(
    test_client: AsyncClient,
    create_test_users: Callable[[list[str]], Coroutine[None, None, list[User]]],
) -> None:
    await create_test_users(["amy", "bob", "carl", "dave", "eddie", "fiona", "gayle"])

    response = await test_client.get("/api/v1/users?page=1&page_size=5")

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

    response = await test_client.get("/api/v1/users?page=2&page_size=5")

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
