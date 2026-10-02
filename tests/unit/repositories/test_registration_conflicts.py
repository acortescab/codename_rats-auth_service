from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from app.core.exceptions.auth import InvalidRegistration
from app.repositories.player_repository import PlayerRepository


def _repo_with_integrity_error():
    write_db = MagicMock()
    write_db.commit.side_effect = IntegrityError("INSERT", {}, Exception("duplicate key"))
    return PlayerRepository(write_db, MagicMock()), write_db


def test_create_user_duplicate_email_raises_invalid_registration():
    """A unique-constraint violation on signup must become a 409, not a 500."""
    repo, write_db = _repo_with_integrity_error()

    with pytest.raises(InvalidRegistration):
        repo.create_user("a@b.com", "Alice", "abcdefg1")

    write_db.rollback.assert_called_once()


def test_upgrade_guest_duplicate_email_raises_invalid_registration():
    repo, write_db = _repo_with_integrity_error()

    with pytest.raises(InvalidRegistration):
        repo.upgrade_guest("id", "a@b.com", "abcdefg1", "Alice")

    write_db.rollback.assert_called_once()


def test_update_last_login_unknown_player_is_a_noop():
    write_db = MagicMock()
    write_db.query.return_value.filter.return_value.first.return_value = None
    repo = PlayerRepository(write_db, MagicMock())

    repo.update_last_login("missing")

    write_db.commit.assert_not_called()
