from typing import cast
from unittest.mock import create_autospec

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.exceptions.auth import InvalidCredentials, InvalidRegistration, InvalidToken
from app.dependencies import get_auth_service, get_token_service
from app.main import app
from app.services.auth_service import AuthService
from app.services.token_service import TokenService


@pytest.mark.asyncio
async def test_guest_login_missing_device_id_returns_422():
    """
    Missing device should return 422
    """
    transport = ASGITransport(app=app, raise_app_exceptions=False)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/v0/auth/guest-login",
            json={}
        )

    assert response.status_code == 422

@pytest.mark.asyncio
async def test_register_email_format_returns_422():
    """
    Invalid email format should return 422
    """
    transport = ASGITransport(app=app, raise_app_exceptions=False)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/v0/auth/register",
            json={
                "email":"email",
                "name":"newuser",
                "password":"213daszz!d"
            }
        )

    assert response.status_code == 422

@pytest.mark.asyncio
async def test_password_format_returns_422():
    """
    Invalid password format should return 422
    """
    transport = ASGITransport(app=app, raise_app_exceptions=False)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/v0/auth/register",
            json={
                "email":"email",
                "name":"newuser",
                "password":"d"
            }
        )

    assert response.status_code == 422

@pytest.mark.asyncio
async def test_me_missing_token_returns_401():
    """
    Missing accesso token in header should return 401
    """
    transport = ASGITransport(app=app, raise_app_exceptions=False)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/v0/auth/me")

    assert response.status_code == 401

@pytest.mark.asyncio
async def test_me_invalid_token_returns_401():
    """
    Invalid access token in header should return 401
    """
    auth_service_mock = cast(AuthService, create_autospec(AuthService))
    auth_service_mock.me.side_effect = InvalidToken("Invalid token")

    app.dependency_overrides[get_auth_service] = lambda: auth_service_mock

    transport = ASGITransport(app=app, raise_app_exceptions=False)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/v0/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )

    assert response.status_code == 401

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_refresh_invalid_token_returns_401():
    """
    Invalid refresh token should return 401
    """
    token_service_mock = cast (TokenService, create_autospec(TokenService))
    token_service_mock.refresh_token.side_effect = InvalidToken("Invalid refresh token")
    app.dependency_overrides[get_token_service] = lambda: token_service_mock

    auth_service_mock = cast(AuthService, create_autospec(AuthService))
    app.dependency_overrides[get_auth_service] = lambda: auth_service_mock

    transport = ASGITransport(app=app, raise_app_exceptions=False)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/v0/auth/refresh-token",
            json={"refresh_token": "bad_token"}
        )

    assert response.status_code == 401

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_guest_login_service_exception_returns_500():
    """
    DB down should return 500
    """
    auth_service_mock = cast(AuthService, create_autospec(AuthService))
    auth_service_mock.guest_login.side_effect = Exception("DB down")

    app.dependency_overrides[get_auth_service] = lambda: auth_service_mock

    transport = ASGITransport(app=app, raise_app_exceptions=False)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/v0/auth/guest-login",
            json={"device_id": "device_123"}
        )

    assert response.status_code == 500

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_register_user_service_exception_returns_409():
    """
    Email duplication should return 409
    """
    auth_service_mock = cast(AuthService, create_autospec(AuthService))
    auth_service_mock.register_user.side_effect = InvalidRegistration("email invalid")

    app.dependency_overrides[get_auth_service] = lambda: auth_service_mock

    transport = ASGITransport(app=app, raise_app_exceptions=False)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/v0/auth/register",
            json={
                "email":"email@email.com",
                "name":"newuser",
                "password":"213daszz!d"
            }
        )

    assert response.status_code == 409

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_login_exception_returns_401():
    """
    Invalid login credentials should return 401 
    """
    auth_service_mock = cast(AuthService, create_autospec(AuthService))
    auth_service_mock.login.side_effect = InvalidCredentials("email invalid")

    app.dependency_overrides[get_auth_service] = lambda: auth_service_mock

    transport = ASGITransport(app=app, raise_app_exceptions=False)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/v0/auth/register",
            json={
                "email":"email@email.com",
                "password":"1111111"
            }
        )

    assert response.status_code == 401

    app.dependency_overrides.clear()