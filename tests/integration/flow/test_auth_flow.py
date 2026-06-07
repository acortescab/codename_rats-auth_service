import pytest

from app.db.session import get_read_db, get_write_db


@pytest.mark.asyncio
async def test_guest_login_persists_in_db(async_client, get_app, db_session_writer, db_session_reader):
    """
    Integration test with real DB validation + isolation.
    """

    def override_get_reader_db():
        yield db_session_reader

    def override_get_writer_db():
        yield db_session_writer

    # Override get_write_db/get_read_db functions used by the app 'default' behaviour
    # to work with the rollback session db for this test
    get_app.dependency_overrides[get_write_db] = override_get_writer_db
    get_app.dependency_overrides[get_read_db] = override_get_reader_db 

    response = await async_client.post(
        "/v0/auth/guest-login",
        json={"device_id": "device_123"}
    )

    assert response.status_code == 200

    from app.repositories.player_repository import PlayerRepository

    repo = PlayerRepository(db_session_writer, db_session_reader)

    player = repo.get_by_device_id("device_123")

    assert player is not None

    # revert functions override
    get_app.dependency_overrides.clear()