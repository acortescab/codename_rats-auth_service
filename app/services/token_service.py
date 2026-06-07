from jose import jwt
from app.core.config import get_settings
from datetime import datetime, timedelta, timezone
from app.repositories.refresh_token_repository import RefreshTokenRepository

class TokenService:
    """
    Service class for handling token-related operations, such as creating access and refresh tokens. This class provides methods to generate tokens based on player IDs, which can be used for authentication and session management in the application.
    """
    def __init__(self, repo: RefreshTokenRepository):
        """
        Initializes the TokenService with necessary configurations. This is a placeholder implementation and should be replaced with actual configuration loading logic.
        """
        self.settings = get_settings()
        self.repo = repo
    
    def create_access_token(self, player_id: int) -> str:
        """
        Creates an access token for the given player ID. This is a placeholder implementation and should be replaced with actual token generation logic.
        """
        payload = {
            "sub": str(player_id),
            "type": "access",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
            "iat": datetime.now(timezone.utc)
        }

        return jwt.encode(payload, self.settings.SECRET_KEY, algorithm=self.settings.ALGORITHM)

    def create_refresh_token(self, player_id: int) -> str:
        """
        Creates a refresh token for the given player ID. This is a placeholder implementation and should be replaced with actual token generation logic.
        """
        exp = datetime.now(timezone.utc) + timedelta(days=7)
        payload = {
            "sub": str(player_id),
            "type": "refresh",
            "exp": exp,
            "iat": datetime.now(timezone.utc)
        }

        token = jwt.encode(payload, self.settings.SECRET_KEY, algorithm=self.settings.ALGORITHM)
        self.repo.create(player_id, token, exp)

        return token

    def decode_token(self, token: str):
        """
        Decodes a token and returns the payload. This is a placeholder implementation and should be replaced with actual token decoding logic.
        """
        return jwt.decode(
            token,
            self.settings.SECRET_KEY,
            algorithms=[self.settings.ALGORITHM]
        )