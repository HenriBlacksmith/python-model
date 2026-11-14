lazy from httpx2 import AsyncClient


async def test_openapi_docs(test_client: AsyncClient) -> None:
    response = await test_client.get("/openapi.json")

    assert response.status_code == 200
    schema = response.json()
    assert all(
        "422" not in operation.get("responses", {})
        for path_item in schema["paths"].values()
        for operation in path_item.values()
        if isinstance(operation, dict)
    )
