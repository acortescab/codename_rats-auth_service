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


def test_create_guest_concurrent_duplicate_device_is_rejected():
    """Two first logins racing on the same device_id: the loser must not get a second account."""
    from app.core.exceptions.auth import InvalidCredentials

    repo, write_db = _repo_with_integrity_error()

    with pytest.raises(InvalidCredentials):
        repo.create_guest("device_12345", "guest-abc", "hash")

    write_db.rollback.assert_called_once()


@pytest.mark.parametrize("rows,expected", [(1, True), (0, False)])
def test_set_device_secret_if_unset_reports_whether_it_won(rows, expected):
    write_db = MagicMock()
    write_db.query.return_value.filter.return_value.update.return_value = rows
    repo = PlayerRepository(write_db, MagicMock())

    assert repo.set_device_secret_if_unset("player-id", "hash") is expected
    write_db.commit.assert_called_once()
