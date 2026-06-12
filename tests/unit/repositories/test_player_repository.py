from app.repositories.player_repository import PlayerRepository


def test_player_repository_create_and_get(db_session_writer, db_session_reader):
    """
    Unit test for creating a new guest-user.
    """
    repo = PlayerRepository(db_session_writer, db_session_reader)

    created = repo.create_guest(
        device_id="device_123",
        name="guest-abc"
    )

    player = repo.get_by_device_id("device_123")

    assert player is not None
    assert player.id == created.id
    assert player.device_id == "device_123"

def test_update_last_login(db_session_writer, db_session_reader):
    """
    Unit test for updating last login timestamp.
    """
    repo = PlayerRepository(db_session_writer, db_session_reader)

    player = repo.create_guest(
        device_id="device_999",
        name="guest-test"
    )

    repo.update_last_login(player.id)

    updated = repo.get_by_device_id("device_999")

    assert updated.last_login is not None

def test_register_user(db_session_writer, db_session_reader):
    """
    Unit test creating a new registered-user
    """
    repo = PlayerRepository(db_session_writer, db_session_reader)

    created = repo.create_user(
        email="email@email.com",
        name="registered_user",
        password="basd13.z112"
    )

    player = repo.get_by_email("email@email.com")

    assert player is not None
    assert player.account_type == "registered"
    assert player.id == created.id