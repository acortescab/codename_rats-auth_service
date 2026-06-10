import uuid
from datetime import datetime, timedelta, timezone

from jose import jwt

from app.core.config import get_settings
from app.core.exceptions.auth import InvalidRefreshTokenError, InvalidToken
from app.repositories.refresh_token_repository import RefreshTokenRepository


class TokenService:
    """
    Service class for handling token-related operations, such as creating access and refresh tokens. 
    This class provides methods to generate tokens based on player IDs, 
    which can be used for authentication and session management in the application.
    """
    def __init__(self, repo: RefreshTokenRepository):
        """
        Initializes the TokenService with necessary configurations.
        """
        self.settings = get_settings()
        self.repo = repo
    
    def create_access_token(self, player_id: int) -> str:
        """
        Creates an access token for the given player ID. 
        """
        payload = {
            "sub": str(player_id),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
            "iat": datetime.now(timezone.utc)
        }

        return jwt.encode(payload, self.settings.SECRET_KEY, algorithm=self.settings.ALGORITHM)
    
    def refresh_token(self, refresh_token: str):
        """
        Create a new refresh token and marks previous as revoked
        """
        token = self.decode_token(refresh_token)

        if not token:
            raise InvalidRefreshTokenError("Invalid token")
        
        player_id = token["sub"]
        stored = self.get_token_by_jti(token["jti"])

        if not stored or stored.revoked:
            raise InvalidRefreshTokenError("Not found or invalid token")

        access_token = self.create_access_token(player_id)
        refresh_token = self.create_refresh_token(player_id) 

        self.repo.revoke_by_id(stored.id)

        return {
            "access_token" : access_token,
            "refresh_token" : refresh_token
        }

    def create_refresh_token(self, player_id: int) -> str:
        """
        Creates a refresh token for the given player ID. 
        """

        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        jti = str(uuid.uuid4())

        payload = {
            "sub": str(player_id),
            "jti": jti,
            "exp": expires_at,
            "iat": datetime.now(timezone.utc)
        }

        token = jwt.encode(payload, self.settings.SECRET_KEY, algorithm=self.settings.ALGORITHM)
        self.repo.create(player_id, jti, token, expires_at)

        return token

    def decode_token(self, token):
        """
        Decodes a token and returns the payload. 
        """
        return jwt.decode(
            token,
            self.settings.SECRET_KEY,
            algorithms=[self.settings.ALGORITHM]
        )
    
    def get_token_by_jti(self, jti: str):
        """
        Get refresh token by jti
        """
        return self.repo.get_by_jti(jti)
    
    def get_and_revoke_token(self, jti: str):
        """
        Revokes token by jti
        """
        revoked = self.repo.revoke_by_jti(jti)

        if not revoked:
            raise InvalidToken("Invalid or revoked token")
    

