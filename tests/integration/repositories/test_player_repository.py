

def test_player_repository_create_and_get(db_session_writer, db_session_reader):
    """
    Integration test for PlayerRepository.

    Verifies:
    - player is persisted in DB
    - player can be retrieved by device_id
    """

    from app.repositories.player_repository import PlayerRepository

    repo = PlayerRepository(db_session_writer, db_session_reader)

    created = repo.create(
        device_id="device_123",
        name="guest-abc"
    )

    player = repo.get_by_device_id("device_123")

    print (f"Player created {player}")

    assert player is not None
    assert player.id == created.id
    assert player.device_id == "device_123"

def test_update_last_login(db_session_writer, db_session_reader):
    """
    Integration test for updating last login timestamp.
    """

    from app.repositories.player_repository import PlayerRepository

    repo = PlayerRepository(db_session_writer, db_session_reader)

    player = repo.create(
        device_id="device_999",
        name="guest-test"
    )

    repo.update_last_login(player)

    updated = repo.get_by_device_id("device_999")

    assert updated.last_login is not None