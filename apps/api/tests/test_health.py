import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


async def test_health(client):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "0.0.1"


async def test_me_dev_mode(client):
    response = await client.get("/api/v1/me")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "dev@local"
