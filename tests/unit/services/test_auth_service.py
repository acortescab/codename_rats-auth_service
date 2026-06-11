import uuid
from typing import cast
from unittest.mock import create_autospec

import pytest
from fastapi.security import HTTPAuthorizationCredentials

from app.core.exceptions.auth import InvalidToken
from app.db.models.player import Player
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.schemas.auth import GuestLoginResponse
from app.services.auth_service import AuthService
from app.services.player_service import PlayerService
from app.services.token_service import TokenService


def test_guest_login_success():
    """
    Tests that guest_login returns a valid AuthResponse
    when a valid device_id is provided.

    This test verifies:
    - PlayerService is called correctly
    - TokenService generates both tokens
    - Response structure is correct
    """
    # Arrange mock dependencies
    player_service = cast(PlayerService, create_autospec(PlayerService))
    token_service = cast(TokenService, create_autospec(TokenService))
    mock_player = cast(Player, create_autospec(Player))

    # Fill mock player data
    mock_player.id = uuid.uuid4()
    mock_player.name = "guest_123"

    # Fill mock player service data
    player_service.get_or_create_guest.return_value = mock_player

    # Fill mock token service data
    token_service.create_access_token.return_value = "access_token_mock"
    token_service.create_refresh_token.return_value = "refresh_token_mock"

    auth_service = AuthService(player_service, token_service)

    # Act
    result = auth_service.guest_login("device_123")

    # Assert
    player_service.get_or_create_guest.assert_called_once_with("device_123")
    token_service.create_access_token.assert_called_once_with(mock_player.id)
    token_service.create_refresh_token.assert_called_once_with(mock_player.id)

    assert isinstance(result, GuestLoginResponse)
    assert result.id == mock_player.id
    assert result.name == mock_player.name
    assert result.access_token == "access_token_mock"
    assert result.refresh_token == "refresh_token_mock"

def test_guest_login_calls_services_once():
    """
    Ensures that all dependencies are called exactly once.

    This protects against:
    - accidental multiple DB calls
    - duplicate token generation
    - unintended side effects
    """

    # Arrange mock dependencies
    player_service = cast(PlayerService, create_autospec(PlayerService))
    token_service = cast(TokenService, create_autospec(TokenService))
    mock_player = cast(Player, create_autospec(Player))

    # Fill mock player data
    mock_player.id = uuid.uuid4()
    mock_player.name = "guest_test"

    # Fill mock player service data
    player_service.get_or_create_guest.return_value = mock_player

    # Fill mock token service data
    token_service.create_access_token.return_value = "a"
    token_service.create_refresh_token.return_value = "b"

    auth_service = AuthService(player_service, token_service)

    # Act
    auth_service.guest_login("device_x")

    assert player_service.get_or_create_guest.call_count == 1
    assert token_service.create_access_token.call_count == 1
    assert token_service.create_refresh_token.call_count == 1

def test_guest_login_empty_device_id_raises_error():
    """
    Tests that guest_login raises ValueError when
    device_id is empty or invalid.

    This ensures input validation is enforced
    at the service layer.
    """

    player_service = cast(PlayerService, create_autospec(PlayerService))
    token_service = cast(TokenService, create_autospec(TokenService))

    service = AuthService(player_service, token_service)

    with pytest.raises(ValueError):
        service.guest_login("")

def test_me_success():
    """
    Tests that /me returns player data when token is valid
    """

    # Arrange
    token_service = cast(TokenService, create_autospec(TokenService))
    player_service = cast(PlayerService, create_autospec(PlayerService))

    payload = {
        "sub": uuid.uuid4()
    }

    token_service.decode_token.return_value = payload

    mock_player = cast(Player, create_autospec(Player))
    mock_player.id = payload["sub"]
    mock_player.name = "test"

    player_service.get_player_by_id.return_value = mock_player

    auth_service = AuthService(player_service, token_service)

    # Act
    result = auth_service.get_player_from_token("valid_token")

    # Assert
    token_service.decode_token.assert_called_once_with("valid_token")
    player_service.get_player_by_id.assert_called_once_with(payload["sub"])

    assert result.id == mock_player.id
    assert result.name == mock_player.name

def test_logout_refresh_token():
    """
    Tests that logout revokes a single refresh token
    """

    # Arrange
    token_service = cast(TokenService, create_autospec(TokenService))
    token_repo = cast(RefreshTokenRepository, create_autospec(RefreshTokenRepository))

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="refresh_token"
    )

    payload = {"jti": "token_123"}

    token_service.decode_token.return_value = payload
    token_repo.revoke_by_jti.return_value = True

    auth_service = AuthService(None, token_service)

    # Act
    auth_service.logout_player(credentials)

    # Assert
    token_service.decode_token.assert_called_once_with(credentials)
    token_service.get_and_revoke_token.assert_called_once_with("token_123")

def test_me_invalid_token():
    """
    Tests that /me raises error when token is invalid
    """

    # Arrange
    token_service = cast(TokenService, create_autospec(TokenService))
    player_service = cast(PlayerService, create_autospec(PlayerService))

    token_service.decode_token.return_value = None

    auth_service = AuthService(player_service, token_service)

    # Act / Assert
    try:
        auth_service.get_player_from_token("bad_token")
        assert False
    except InvalidToken:
        token_service.decode_token.assert_called_once()