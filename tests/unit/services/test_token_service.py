import uuid
from typing import cast
from unittest.mock import create_autospec, patch

import pytest

from app.core.exceptions.auth import InvalidToken
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.services.token_service import TokenService


def test_create_access_token_returns_token():
    """
    Tests that create_access_token returns a JWT string
    and encodes correct payload structure.

    This test mocks JWT encoding to isolate logic.
    """
    # Arrange
    repo = cast(RefreshTokenRepository, create_autospec(RefreshTokenRepository))
    service = TokenService(repo)

    with patch("app.services.token_service.jwt.encode") as mock_encode:
        mock_encode.return_value = "access_token"

        # Act
        token = service.create_access_token(1)

        # Assert
        mock_encode.assert_called_once()

        args, kwargs = mock_encode.call_args
        payload = args[0]

        assert payload["sub"] == "1"
        assert "exp" in payload
        assert "iat" in payload

        assert token == "access_token"

def test_create_refresh_token_saves_to_repository():
    """
    Tests that create_refresh_token:
    - generates a JWT token
    - persists it via RefreshTokenRepository
    """
    # Arrange
    repo = cast(RefreshTokenRepository, create_autospec(RefreshTokenRepository))
    repo.create.return_value = None

    service = TokenService(repo)

    with patch("app.services.token_service.jwt.encode") as mock_encode:
        mock_encode.return_value = "refresh_token"

        # Act
        token = service.create_refresh_token(1)

        # Assert
        mock_encode.assert_called_once()
        repo.create.assert_called_once()

        args = repo.create.call_args.args
        assert args[0] == 1
        assert args[2] == "refresh_token"
        assert args[4] is not None

        assert token == "refresh_token"

def test_decode_token_returns_payload():
    """
    Tests that decode_token correctly calls jwt.decode
    and returns the decoded payload.
    """
    # Arrange
    repo = cast(RefreshTokenRepository, create_autospec(RefreshTokenRepository))
    service = TokenService(repo)

    fake_payload = {
        "sub": "1",
        "type": "access"
    }

    with patch("app.services.token_service.jwt.decode") as mock_decode:
        mock_decode.return_value = fake_payload

        # Act
        result = service.decode_token("fake_token")

        # Assert
        mock_decode.assert_called_once()
        assert result == fake_payload


def test_refresh_token_rotates_valid_token_and_reuses_family_id():
    """A valid refresh token rotates and keeps the same family."""
    repo = cast(RefreshTokenRepository, create_autospec(RefreshTokenRepository))
    service = TokenService(repo)
    family_id = str(uuid.uuid4())

    repo.get_by_jti.return_value = type(
        "StoredToken",
        (),
        {"family_id": family_id, "revoked": False, "jti": "old-jti"},
    )()

    with patch("app.services.token_service.jwt.decode") as mock_decode, patch(
        "app.services.token_service.jwt.encode",
        side_effect=["new_access_token", "new_refresh_token"],
    ):
        mock_decode.return_value = {"sub": "1", "jti": "old-jti"}

        result = service.refresh_token("old_token")

    assert result == {"access_token": "new_access_token", "refresh_token": "new_refresh_token"}
    repo.revoke_by_jti.assert_called_once_with("old-jti")
    assert repo.create.call_args.args[0] == "1"
    assert repo.create.call_args.args[4] == family_id


def test_refresh_token_reuse_invalidates_family():
    """A rotated refresh token cannot be reused; it invalidates the entire family."""
    repo = cast(RefreshTokenRepository, create_autospec(RefreshTokenRepository))
    service = TokenService(repo)
    family_id = str(uuid.uuid4())

    repo.get_by_jti.return_value = type(
        "StoredToken",
        (),
        {"family_id": family_id, "revoked": True, "jti": "old-jti"},
    )()

    with patch("app.services.token_service.jwt.decode") as mock_decode:
        mock_decode.return_value = {"sub": "1", "jti": "old-jti"}

        with pytest.raises(InvalidToken, match="family"):
            service.refresh_token("reused_token")

    repo.revoke_by_family_id.assert_called_once_with(family_id)