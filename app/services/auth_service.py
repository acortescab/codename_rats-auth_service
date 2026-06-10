import logging

from app.core.exceptions.auth import InvalidToken
from app.schemas.auth import GuestLoginResponse, MeResponse
from app.services.player_service import PlayerService
from app.services.token_service import TokenService

logger = logging.getLogger("__name__")

class AuthService:
    """
    Service class for handling authentication-related operations, such as guest login. 
    This class interacts with the PlayerRepository to manage player data and uses token 
    generation functions to create access and refresh tokens for authenticated players.
    """
    def __init__(self, player_service: PlayerService, token_service: TokenService):
        """
        Initializes the AuthService with a PlayerService and TokenService instance.
        """
        self.player_service = player_service
        self.token_service = token_service

    def guest_login(self, device_id: str):
        """
        Handles guest login by checking for an existing player with the given device ID or creating a new one if none exists.
        Generates access and refresh tokens for the player and returns an AuthResponse 
        containing the player's information and tokens.
        """
        player = self.player_service.get_or_create_guest(device_id)

        access_token = self.token_service.create_access_token(player.id)
        refresh_token = self.token_service.create_refresh_token(player.id)

        return GuestLoginResponse(
            id=player.id, 
            name=player.name,
            access_token=access_token, 
            refresh_token=refresh_token
        )
    
    def get_player_from_token(self, token: str):
        """
        Returns player from token
        """
        payload = self.token_service.decode_token(token)

        if not payload:
            logger.info(f"payload decoding error for token: {token}")
            raise InvalidToken("Invalid token")

        player = self.player_service.get_player_by_id(payload["sub"])
        logger.info(f"user valid for token: {token}")

        return MeResponse(
            id=player.id,
            name=player.name
        )
    
    def logout_player(self, token: str):
        """
        Logouts a player with valid token revoking it
        """
        payload = self.token_service.decode_token(token)

        if not payload:
            logger.info(f"payload decoding error for token: {token}")
            raise InvalidToken("Invalid token")
        
        logger.info(f"token valid: {payload}")
        
        jti = payload.get("jti")
        if not jti:
            logger.info(f"payload jti error: {payload}")
            raise InvalidToken("Invalid token")
        
        self.token_service.get_and_revoke_token(jti)
        
