import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.mark.asyncio
async def test_health_check_integration():
    """
    Integration test for health endpoint.

    Verifies full stack:
    - FastAPI app
    - Router
    - Response serialization
    """

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/v0/health/")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["version"] == "v0"