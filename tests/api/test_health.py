from fastapi.testclient import TestClient


def test_health(test_client: TestClient):
    response = test_client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "pass"}
