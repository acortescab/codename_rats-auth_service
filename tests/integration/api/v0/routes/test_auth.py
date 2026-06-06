import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app

@pytest.mark.asyncio
async def test_guest_login_integration():
    """
    Full integration test for guest login endpoint.

    This tests:
    - FastAPI routing
    - Pydantic validation
    - Dependency injection
    - AuthService flow (real logic)
    """

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:

        payload = {
            "device_id": "device_123"
        }

        response = await client.post(
            "/auth/guest-login",
            json=payload
        )

    assert response.status_code == 200

    data = response.json()

    assert "id" in data
    assert "name" in data
    assert "access_token" in data
    assert "refresh_token" in data