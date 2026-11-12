from unittest.mock import ANY
from uuid import uuid4
lazy from collections.abc import Callable, Coroutine

import pytest
lazy from httpx2 import AsyncClient

lazy from app.adapters.database.models import User


async def test_successful_user_creation(test_client: AsyncClient) -> None:
    response = await test_client.post(
        "/api/v1/users",
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


async def test_user_creation_with_invalid_username(test_client: AsyncClient) -> None:
    response = await test_client.post(
        "/api/v1/users",
        json={
            "username": "",
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "status": 400,
        "title": "The request was invalid.",
        "type": "about:blank",
        "detail": "",
        "instance": "/api/v1/users",
    }
    assert response.headers["content-type"] == "application/problem+json"


async def test_successful_user_retrieval(
    test_client: AsyncClient, test_user: User
) -> None:
    response = await test_client.get(f"/api/v1/users/{test_user.id}")

    assert response.status_code == 200
    assert response.json() == {
        "username": test_user.name,
        "userId": str(test_user.id),
        "createdAt": ANY,
        "updatedAt": ANY,
    }


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
async def test_successful_user_list_multiple_users(
    test_client: AsyncClient,
    query: str,
    create_test_users: Callable[[list[str]], Coroutine[None, None, list[User]]],
) -> None:
    users = await create_test_users(
        ["amy", "bob", "carl", "dave", "eddie", "fiona", "gayle"]
    )

    response = await test_client.get(f"/api/v1/users?{query}")

    assert response.status_code == 200
    body = response.json()
    assert body["pageSize"] == 10
    assert body["page"] == 1
    assert body["total"] == len(users)
    assert sorted(user["username"] for user in body["data"]) == sorted(
        user.name for user in users
    )
    assert body["links"] == {
        "self": "http://blacksmith.local/api/v1/users?page=1&page_size=10",
        "first": "http://blacksmith.local/api/v1/users?page=1&page_size=10",
        "last": "http://blacksmith.local/api/v1/users?page=1&page_size=10",
        "prev": None,
        "next": None,
    }


async def test_retrieval_of_non_existent_user(test_client: AsyncClient) -> None:
    random_id = uuid4()
    response = await test_client.get(f"/api/v1/users/{random_id}")

    assert response.status_code == 404
    assert response.json() == {
        "type": "about:blank",
        "status": 404,
        "title": "User not found.",
        "instance": f"/api/v1/users/{random_id}",
    }
    assert response.headers["content-type"] == "application/problem+json"


async def test_successful_user_update(
    test_client: AsyncClient, test_user: User
) -> None:
    response = await test_client.put(
        f"/api/v1/users/{test_user.id}",
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


async def test_successful_user_deletion(
    test_client: AsyncClient, test_user: User
) -> None:
    response = await test_client.delete(f"/api/v1/users/{test_user.id}")

    assert response.status_code == 204
    assert response.content == b""
