import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_root():
    """
    Test the root endpoint to ensure it returns the expected status and service information.
    """
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "OAuth"
    assert "env" in data


@pytest.mark.asyncio
async def test_jwks_endpoint_returns_public_key_set():
    """The app must expose a JWKS document for other services to validate tokens."""
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/.well-known/jwks.json")

    assert response.status_code == 200
    payload = response.json()

    assert "keys" in payload
    assert isinstance(payload["keys"], list)
    assert len(payload["keys"]) > 0

    key = payload["keys"][0]
    assert key["kty"] == "RSA"
    assert key["use"] == "sig"
    assert key["alg"] == "RS256"
    assert "n" in key
    assert "e" in key