from typing import cast
from unittest.mock import create_autospec, patch

from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.services.token_service import TokenService


def test_create_access_token_returns_token():
    """
    Tests that create_access_token returns a JWT string
    and encodes correct payload structure.

    This test mocks JWT encoding to isolate logic.
    """

    repo = cast(RefreshTokenRepository, create_autospec(RefreshTokenRepository))
    service = TokenService(repo)

    with patch("app.services.token_service.jwt.encode") as mock_encode:
        mock_encode.return_value = "access_token"

        token = service.create_access_token(1)

        mock_encode.assert_called_once()

        args, kwargs = mock_encode.call_args
        payload = args[0]

        assert payload["sub"] == "1"
        assert "jti" in payload
        assert "exp" in payload
        assert "iat" in payload

        assert token == "access_token"

def test_create_refresh_token_saves_to_repository():
    """
    Tests that create_refresh_token:
    - generates a JWT token
    - persists it via RefreshTokenRepository
    """

    repo = cast(RefreshTokenRepository, create_autospec(RefreshTokenRepository))
    repo.create.return_value = None

    service = TokenService(repo)

    with patch("app.services.token_service.jwt.encode") as mock_encode:
        mock_encode.return_value = "refresh_token"

        token = service.create_refresh_token(1)

        # JWT generation check
        mock_encode.assert_called_once()

        # Repository interaction check
        repo.create.assert_called_once()

        assert token == "refresh_token"

def test_decode_token_returns_payload():
    """
    Tests that decode_token correctly calls jwt.decode
    and returns the decoded payload.
    """

    repo = cast(RefreshTokenRepository, create_autospec(RefreshTokenRepository))
    service = TokenService(repo)

    fake_payload = {
        "sub": "1",
        "type": "access"
    }

    with patch("app.services.token_service.jwt.decode") as mock_decode:
        mock_decode.return_value = fake_payload

        result = service.decode_token("fake_token")

        mock_decode.assert_called_once()
        assert result == fake_payload