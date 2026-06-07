

def test_refresh_token_persistence(db_session_writer, db_session_reader):
    """
    Integration test for RefreshTokenRepository.

    Verifies:
    - token is stored in DB
    - can be retrieved later
    """

    from app.repositories.refresh_token_repository import RefreshTokenRepository
    from app.repositories.player_repository import PlayerRepository
    from datetime import datetime, timedelta, timezone
    import hashlib

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