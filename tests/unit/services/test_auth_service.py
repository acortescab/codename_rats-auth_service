import pytest
from unittest.mock import Mock
from app.services.auth_service import AuthService
from app.schemas.auth import AuthResponse

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
    player_service = Mock()
    token_service = Mock()
    mock_player = Mock()

    # Fill mock player data
    mock_player.id = 1
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
    token_service.create_access_token.assert_called_once_with(1)
    token_service.create_refresh_token.assert_called_once_with(1)

    assert isinstance(result, AuthResponse)
    assert result.id == 1
    assert result.name == "guest_123"
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
    player_service = Mock()
    token_service = Mock()
    mock_player = Mock()

    # Fill mock player data
    mock_player.id = 99
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

    player_service = Mock()
    token_service = Mock()

    service = AuthService(player_service, token_service)

    with pytest.raises(ValueError):
        service.guest_login("")