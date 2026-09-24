import uuid
from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import get_settings
from app.core.exceptions.auth import InvalidToken
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

        return self.encode_token(payload)
    
    def refresh_token(self, refresh_token: str):
        """
        Create a new refresh token and marks previous as revoked.
        If a token from the same family is reused after rotation, revoke the whole family.
        """
        token = self.decode_token(refresh_token)

        if not token:
            raise InvalidToken("Invalid token")
        
        player_id = token.get("sub")
        jti = token.get("jti")

        if not player_id or not jti:
            raise InvalidToken("Invalid token")

        stored = self.get_token_by_jti(jti, include_revoked=True)

        if not stored:
            raise InvalidToken("Not found or invalid token")

        if stored.revoked:
            if stored.family_id:
                self.repo.revoke_by_family_id(stored.family_id)
            raise InvalidToken("Refresh token reused; family invalidated")

        family_id = stored.family_id or str(uuid.uuid4())

        access_token = self.create_access_token(player_id)
        new_refresh_token = self.create_refresh_token(player_id, family_id)

        self.repo.revoke_by_jti(jti)

        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token
        }

    def create_refresh_token(self, player_id: int, family_id: str = None) -> str:
        """
        Creates a refresh token for the given player ID.
        Each refresh-token family shares the same family_id across rotations.
        """
        family_id = family_id or str(uuid.uuid4())
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        jti = str(uuid.uuid4())

        payload = {
            "sub": str(player_id),
            "jti": jti,
            "family_id": str(family_id),
            "exp": expires_at,
            "iat": datetime.now(timezone.utc)
        }

        token = self.encode_token(payload)
        self.repo.create(player_id, jti, token, expires_at, family_id)

        return token

    def encode_token(self, payload: dict) -> str:
        """
        Encodes a payload into a JWT token.
        """
        return jwt.encode(payload, self.settings.SECRET_KEY, algorithm=self.settings.ALGORITHM)

    def decode_token(self, token):
        """
        Decodes a token and returns the payload using the matching public key.
        """
        return jwt.decode(token, self.settings.public_key_pem, algorithms=[self.settings.ALGORITHM])
    
    def get_token_by_jti(self, jti: str, include_revoked: bool = False):
        """
        Get refresh token by jti.
        """
        return self.repo.get_by_jti(jti, include_revoked=include_revoked)
    
    def revoke_token_by_jti(self, jti: str):
        """
        Revokes token by jti
        """
        revoked = self.repo.revoke_by_jti(jti)

        if not revoked:
            raise InvalidToken("Invalid or revoked token")
        
    def revoke_token_by_player_id(self, player_id: int):
        """
        Revokes token by player_id
        """
        self.repo.revoke_by_player_id(player_id)

    def revoke_token_by_family_id(self, family_id):
        """
        Revokes all tokens from a family.
        """
        self.repo.revoke_by_family_id(family_id)
    

