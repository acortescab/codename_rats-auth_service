import pytest

from app.db.models.player import Player
from app.db.session import get_read_db, get_write_db


@pytest.mark.asyncio
async def test_guest_login_persists_in_db(async_client, get_app, db_session_writer):
    """
    E2E test with real DB validation + isolation for guest login
    """
    # Override get_write_db/get_read_db functions used by the app 'default' behaviour
    # to work with the rollback session db for this test
    get_app.dependency_overrides[get_write_db] = lambda: db_session_writer
    get_app.dependency_overrides[get_read_db] = lambda: db_session_writer

    try:
        response = await async_client.post(
            "/v0/auth/guest-login",
            json={"device_id": "device_123"}
        )

        assert response.status_code == 200

        player = db_session_writer.query(Player).filter_by(
            device_id="device_123"
        ).first()

        assert player is not None
    finally:
        # revert functions override
        get_app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_register_persists_in_db(async_client, get_app, db_session_writer):
    """
    E2E test with real DB validation + isolation for register
    """
    # Override get_write_db/get_read_db functions used by the app 'default' behaviour
    # to work with the rollback session db for this test
    get_app.dependency_overrides[get_write_db] = lambda: db_session_writer
    get_app.dependency_overrides[get_read_db] = lambda: db_session_writer

    try:
        response = await async_client.post(
            "/v0/auth/register",
            json={
                "email":"email@email.com",
                "name":"newuser",
                "password":"213daszz!d"
            }
        )

        assert response.status_code == 200

        player = db_session_writer.query(Player).filter_by(
            email="email@email.com"
        ).first()

        assert player is not None
    finally:
        # revert functions override
        get_app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_register_same_email(async_client, get_app, db_session_writer):
    """
    E2E test with real DB multiple times with the same email
    """
    # Override get_write_db/get_read_db functions used by the app 'default' behaviour
    # to work with the rollback session db for this test
    get_app.dependency_overrides[get_write_db] = lambda: db_session_writer
    get_app.dependency_overrides[get_read_db] = lambda: db_session_writer

    try:
        response = await async_client.post(
            "/v0/auth/register",
            json={
                "email":"email@email.com",
                "name":"newuser",
                "password":"213daszz!d"
            }
        )

        assert response.status_code == 200

        response = await async_client.post(
            "/v0/auth/register",
            json={
                "email":"email@email.com",
                "name":"newuser",
                "password":"213daszz!d"
            }
        )

        assert response.status_code == 409
    finally:
        # revert functions override
        get_app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_auth_full_lifecycle(async_client, get_app, db_session_writer):
    """
    E2E test with full auth lifecycle (login-me-refresh-logout)
    """
    # Override get_write_db/get_read_db functions used by the app 'default' behaviour
    # to work with the rollback session db for this test
    get_app.dependency_overrides[get_write_db] = lambda: db_session_writer
    get_app.dependency_overrides[get_read_db] = lambda: db_session_writer

    try:
        # Login
        login_res = await async_client.post(
            "/v0/auth/guest-login",
            json={"device_id": "device_123"}
        )

        assert login_res.status_code == 200

        login_data = login_res.json()
        access_token = login_data["access_token"]
        refresh_token = login_data["refresh_token"]

        # Me
        me_res = await async_client.get(
            "/v0/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert me_res.status_code == 200

        # Refresh token
        refresh_res = await async_client.post(
            "/v0/auth/refresh-token",
            json={"refresh_token": refresh_token}
        )

        assert refresh_res.status_code == 200

        data = refresh_res.json()
        access_token = data["access_token"]
        refresh_token = data["refresh_token"]

        # Me
        me_res_2 = await async_client.get(
            "/v0/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert me_res_2.status_code == 200

        # Logout
        logout_res = await async_client.post(
            "/v0/auth/logout",
            headers={"Authorization": f"Bearer {refresh_token}"}
        )

        assert logout_res.status_code == 200

        # Refresh should fail post logout
        refresh_fail = await async_client.post(
            "/v0/auth/refresh-token",
            json={"refresh_token": refresh_token}
        )

        assert refresh_fail.status_code == 401

    finally:
        # revert functions override
        get_app.dependency_overrides.clear()

async def test_refresh_token_rejected_after_logout(async_client, get_app, db_session_writer):
    """
    E2E test to avoid token reuse after logout
    """
    # Override get_write_db/get_read_db functions used by the app 'default' behaviour
    # to work with the rollback session db for this test
    get_app.dependency_overrides[get_write_db] = lambda: db_session_writer
    get_app.dependency_overrides[get_read_db] = lambda: db_session_writer

    try:
        login_res = await async_client.post(
            "/v0/auth/guest-login",
            json={"device_id": "device_456"}
        )

        assert login_res.status_code == 200

        data = login_res.json()
        refresh_token = data["refresh_token"]

        logout_res = await async_client.post(
            "/v0/auth/logout",
            headers={"Authorization": f"Bearer {refresh_token}"}
        )

        assert logout_res.status_code == 200

        reuse_res = await async_client.post(
            "/v0/auth/refresh-token",
            json={"refresh_token": refresh_token}
        )

        assert reuse_res.status_code == 401
    finally:
        # revert functions override
        get_app.dependency_overrides.clear()