import pytest
from app.db.session import SessionLocalWriter

@pytest.fixture
def db_session():
    """
    Provides a DB session with automatic rollback.
    """
    session = SessionLocalWriter()

    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.mark.asyncio
async def test_guest_login_persists_in_db(async_client, db_session):
    """
    Integration test with real DB validation + isolation.
    """

    response = await async_client.post(
        "/auth/guest-login",
        json={"device_id": "device_123"}
    )

    assert response.status_code == 200

    from app.repositories.player_repository import PlayerRepository

    repo = PlayerRepository(db_session)

    player = repo.get_by_device("device_123")

    assert player is not None