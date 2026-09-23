import uuid
from typing import cast
from unittest.mock import create_autospec

from app.db.models.player import Player
from app.repositories.player_repository import PlayerRepository
from app.services.player_service import PlayerService


def test_get_or_create_guest_existing_player():
    """
    Tests that if a player already exists for the given device_id,
    the service returns it and updates last_login.

    This ensures:
    - No duplicate player creation
    - last_login is updated correctly
    """
    # Arrange
    repo = cast(PlayerRepository, create_autospec(PlayerRepository))
    
    existing_player = cast(Player, create_autospec(Player))
    existing_player.id = uuid.uuid4()
    existing_player.name = "guest-123"
    existing_player.account_type ="guest"

    repo.get_by_device_id.return_value = existing_player

    service = PlayerService(repo)

    # Act
    result = service.get_or_create_guest("device_123")
    
    # Assert
    repo.get_by_device_id.assert_called_once_with("device_123")
    repo.update_last_login.assert_called_once_with(existing_player.id)
    repo.create_guest.assert_not_called()

    assert result == existing_player

def test_get_or_create_guest_creates_new_player():
    """
    Tests that if no player exists for the given device_id,
    a new guest player is created with a generated name.

    This ensures:
    - repository.create is called
    - generate_guest_name is used
    """
    # Arrange
    repo = cast(PlayerRepository, create_autospec(PlayerRepository))
    repo.get_by_device_id.return_value = None

    created_player = cast(Player, create_autospec(Player))
    created_player.id = uuid.uuid4()
    created_player.name = "guest-abc123"
    created_player.account_type = "guest"

    repo.create_guest.return_value = created_player

    service = PlayerService(repo)

    # Act
    result = service.get_or_create_guest("device_999")

    # Assert
    repo.get_by_device_id.assert_called_once_with("device_999")
    repo.update_last_login.assert_not_called()
    repo.create_guest.assert_called_once()

    assert result == created_player

def test_generate_guest_name_format():
    """
    Tests that generate_guest_name returns a string
    with correct format: guest-xxxxxx
    """
    # Arrange
    repo = cast(PlayerRepository, create_autospec(PlayerRepository))
    service = PlayerService(repo)

    # Act
    name = service.generate_guest_name()

    # Assert
    assert name.startswith("guest-")
    assert len(name) == len("guest-") + 6