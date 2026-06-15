import uuid
from typing import cast
from unittest.mock import create_autospec

import pytest
from fastapi.security import HTTPAuthorizationCredentials

from app.core.exceptions.auth import InvalidRegistration, InvalidToken
from app.core.security import hash_password, verify_password
from app.db.models.player import Player
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.schemas.auth import GuestLoginResponse, LoginResponse, RegisterResponse
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
    # Arrange
    player_service = cast(PlayerService, create_autospec(PlayerService))
    token_service = cast(TokenService, create_autospec(TokenService))
    mock_player = cast(Player, create_autospec(Player))

    mock_player.id = uuid.uuid4()
    mock_player.name = "guest_123"

    player_service.get_or_create_guest.return_value = mock_player

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

def test_guest_login_empty_device_id_raises_error():
    """
    Tests that guest_login raises ValueError when
    device_id is empty or invalid.

    This ensures input validation is enforced
    at the service layer.
    """
    # Arrange
    player_service = cast(PlayerService, create_autospec(PlayerService))
    token_service = cast(TokenService, create_autospec(TokenService))

    service = AuthService(player_service, token_service)

    # Act
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
    result = auth_service.me("valid_token")

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

    # Act
    try:
        auth_service.me("bad_token")
        
        # Assert
        assert False
    except InvalidToken:
        token_service.decode_token.assert_called_once()

def test_register_success():
    """
    Test that register returns a valid RegisteredResponse
    """
    # Arrange
    token_service = cast(TokenService, create_autospec(TokenService))
    player_service = cast(PlayerService, create_autospec(PlayerService))
    mock_player = cast(Player, create_autospec(Player))

    mock_player.id = uuid.uuid4()
    mock_player.name = "user-123"
    mock_player.email = "email@email.com"

    player_service.register_user.return_value = mock_player

    auth_service = AuthService(player_service, token_service)

    # Act
    result = auth_service.register_user("email@email.com", "user-123", "1314rdas.z")

    # Assert
    assert player_service.get_or_create_guest.call_count == 1

    assert isinstance(result, RegisterResponse)
    assert result.id == mock_player.id
    assert result.name == mock_player.name
    assert result.email == mock_player.email

def test_login_success():
    """
    Test that login returns a valid LoginResponse
    """
    # Arrange
    token_service = cast(TokenService, create_autospec(TokenService))
    player_service = cast(PlayerService, create_autospec(PlayerService))

    mock_player = cast(Player, create_autospec(Player))
    mock_player.id = uuid.uuid4()
    mock_player.name = "user_123"
    mock_player.email = "email@email.com"

    player_service.get_player_by_email.return_value = mock_player

    token_service.create_access_token.return_value = "access_token_mock"
    token_service.create_refresh_token.return_value = "refresh_token_mock"

    verify_password.return_value = True
    
    auth_service = AuthService(player_service, token_service)
    
    # Act
    result = auth_service.login("email@email.com", "1314rdas.z")

    # Assert
    assert isinstance(result, LoginResponse)

    assert result.id == mock_player.id
    assert result.name == mock_player.name
    assert result.email == mock_player.email
    assert result.access_token == "access_token_mock"
    assert result.refresh_token == "refresh_token_mock"

def test_link_account_success():
    """
    Guest account should be converted to registered account
    and return new tokens for same player.
    """
    # Arrange
    token_service = cast(TokenService, create_autospec(TokenService))
    player_service = cast(PlayerService, create_autospec(PlayerService))

    mock_player = cast(Player, create_autospec(Player))
    mock_player.id = uuid.uuid4()
    mock_player.account_type = "guest"
    mock_player.device_id ="device_123" 

    player_service.repo.get_by_id.return_value = mock_player
    player_service.repo.get_by_email.return_value = None

    hash_password.hash.return_value = "hashed_password"

    token_service.create_access_token.return_value = "access_token"
    token_service.create_refresh_token.return_value = "refresh_token"

    auth_service = AuthService(player_service, token_service)

    # Act
    result = auth_service.link_account(
        player_id=mock_player.id,
        email="test@example.com",
        password="Password123"
    )

    # Assert
    assert result.access_token == "access_token"
    assert result.refresh_token == "refresh_token"

    player_service.repo.get_by_id.assert_called_once_with(mock_player.id)
    player_service.repo.get_by_email.assert_called_once_with("test@example.com")
    hash_password.hash.assert_called_once_with("Password123")
    player_service.repo.upgrade_guest.assert_called_once()
    token_service.create_access_token.assert_called_once_with(mock_player.id)
    token_service.create_refresh_token.assert_called_once_with(mock_player.id)

def test_link_account_email_already_exists():
    """
    Cannot link account if provided email already exists
    """
    # Arrange
    token_service = cast(TokenService, create_autospec(TokenService))
    player_service = cast(PlayerService, create_autospec(PlayerService))

    mock_player_new = cast(Player, create_autospec(Player))
    mock_player_new.id = uuid.uuid4()
    mock_player_new.account_type = "guest"
    mock_player_new.device_id = "device_123"

    mock_player = cast(Player, create_autospec(Player))
    mock_player.id = uuid.uuid4()
    mock_player.account_type = "registered"
    mock_player.name = "user-123"
    mock_player.email ="test@example.com" 

    player_service.repo.get_by_email.return_value = mock_player

    auth_service = AuthService(player_service, token_service)

    auth_service.get_player_by_token.return_value = mock_player_new

    # Act
    try:
        auth_service.link_account(
            "test@mail.com", 
            "userfake_123", 
            "Password123", 
            "access_token"
        )

        # Assert
        assert False
    except InvalidRegistration:
        assert True

def test_link_account_guest_not_found():
    """
    Cannot link if guest account for this device is not found
    """
    # Arrange
    token_service = cast(TokenService, create_autospec(TokenService))
    player_service = cast(PlayerService, create_autospec(PlayerService))

    auth_service = AuthService(player_service, token_service)

    auth_service.get_player_by_token.return_value = None

    try:
        auth_service.link_account(
            "test@mail.com",
            "userfake_123",
            "Password123",
            "access_token"
        )
        assert False
    except InvalidRegistration:
        assert True