import pytest

from app.db.session import SessionLocalWriter


@pytest.fixture
def db_session():
    """
    Creates a real database session for integration tests.
    """
    session = SessionLocalWriter()

    try:
        yield session
    finally:
        session.rollback()
        session.close()

def test_player_repository_create_and_get(db_session):
    """
    Integration test for PlayerRepository.

    Verifies:
    - player is persisted in DB
    - player can be retrieved by device_id
    """

    from app.repositories.player_repository import PlayerRepository

    repo = PlayerRepository(db_session)

    created = repo.create(
        device_id="device_123",
        name="guest-abc"
    )

    player = repo.get_by_device("device_123")

    assert player is not None
    assert player.id == created.id
    assert player.device_id == "device_123"

def test_update_last_login(db_session):
    """
    Integration test for updating last login timestamp.
    """

    from app.repositories.player_repository import PlayerRepository

    repo = PlayerRepository(db_session)

    player = repo.create(
        device_id="device_999",
        name="guest-test"
    )

    repo.update_last_login(player.id)

    updated = repo.get_by_device("device_999")

    assert updated.last_login is not None