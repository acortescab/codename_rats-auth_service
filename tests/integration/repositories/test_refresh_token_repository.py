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

def test_refresh_token_persistence(db_session):
    """
    Integration test for RefreshTokenRepository.

    Verifies:
    - token is stored in DB
    - can be retrieved later
    """

    from app.repositories.refresh_token_repository import RefreshTokenRepository

    repo = RefreshTokenRepository(db_session)

    token = "hashed_token_123"

    repo.create(
        player_id=1,
        token=token
    )

    stored = repo.get_by_player_id(1)

    assert stored is not None
    assert stored.token == token