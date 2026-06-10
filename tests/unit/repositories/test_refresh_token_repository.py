import hashlib
from datetime import datetime, timedelta, timezone

from app.db.models.refresh_token import RefreshToken
from app.repositories.player_repository import PlayerRepository
from app.repositories.refresh_token_repository import RefreshTokenRepository


def test_get_by_player_id(db_session_writer, db_session_reader):
    """
    Unit test for fetch refresh token by player_id
    """

    token = RefreshToken(
        player_id="player_1",
        jti="jti_123",
        revoked=False
    )

    db_session_writer.add(token)
    db_session_writer.commit()

    repo = RefreshTokenRepository(db_session_writer, db_session_reader)

    result = repo.get_by_player_id("player_1")

    assert result is not None
    assert result.player_id == "player_1"

def test_refresh_token_persistence(db_session_writer, db_session_reader):
    """
    Unit test for RefreshTokenRepository.

    Verifies:
    - token is stored in DB
    - can be retrieved later
    """

    repo_player = PlayerRepository(db_session_writer, db_session_reader)
    repo_token = RefreshTokenRepository(db_session_writer, db_session_reader)

    token = "token_123"
    token_hashed = hashlib.sha256(token.encode()).hexdigest()

    player = repo_player.create(
        device_id="device_123", 
        name = "name_123"
    )

    repo_token.create(
        player_id=player.id,
        token=token,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7)
    )

    stored = repo_token.get_by_player_id(player.id)

    assert stored is not None
    assert stored.token_hash == token_hashed

def test_get_by_jti_returns_valid_token(db_session_writer, db_session_reader):
    """
    Unit test for fetch a valir refresh token by jti
    """
    token = RefreshToken(
        player_id="player_1",
        jti="jti_123",
        revoked=False
    )

    db_session_writer.add(token)
    db_session_writer.commit()

    repo = RefreshTokenRepository(db_session_writer, db_session_reader)

    result = repo.get_by_jti("jti_123")

    assert result is not None
    assert result.jti == "jti_123"
    assert result.revoked is False

def test_get_by_jti_excludes_revoked(db_session_writer, db_session_reader):
    """
    Unit test to check if revoked tokens are excluded from the query
    """
    token = RefreshToken(
        player_id="player_1",
        jti="jti_123",
        revoked=True
    )

    db_session_writer.add(token)
    db_session_writer.commit()

    repo = RefreshTokenRepository(db_session_writer, db_session_reader)

    result = repo.get_by_jti("jti_123")

    assert result is None

def test_revoke_by_jti_success(db_session_writer, db_session_reader):
    """
    Unit test to check if revoke is updating db field
    """
    token = RefreshToken(
        player_id="player_1",
        jti="jti_123",
        revoked=False
    )

    db_session_writer.add(token)
    db_session_writer.commit()

    repo = RefreshTokenRepository(db_session_writer, db_session_reader)

    result = repo.revoke_by_jti("jti_123")

    assert result is True

    updated = db_session_reader.query(RefreshToken).filter_by(
        jti="jti_123"
    ).first()

    assert updated.revoked is True

def test_revoke_by_jti_returns_false_if_not_found(db_session_writer, db_session_reader):
    """
    Unit test to check revoke by jti when this is not found
    """
    repo = RefreshTokenRepository(db_session_writer, db_session_reader)

    result = repo.revoke_by_jti("non_existing")

    assert result is False