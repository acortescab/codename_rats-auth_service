from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.core.exceptions.auth import InvalidRefreshTokenError, InvalidToken
from app.core.security import OAuthDep
from app.dependencies import get_auth_service, get_player_service, get_token_service
from app.schemas.auth import GuestLoginRequest, GuestLoginResponse, MeResponse, RefreshTokenRequest, RefreshTokenResponse
from app.services.auth_service import AuthService, PlayerService, TokenService

# Authentication routes for the OAuth service
router = APIRouter(prefix="/auth", tags=["auth"])

# Resolve Dependency Injection to get multiple services
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
TokenServiceDep = Annotated[TokenService, Depends(get_token_service)]
PlayerServiceDep = Annotated[PlayerService, Depends(get_player_service)]

@router.post("/guest-login", response_model=GuestLoginResponse)
def guest_login(payload: GuestLoginRequest, service: AuthServiceDep):
    """
    Endpoint for guest login.
    """
    return service.guest_login(payload.device_id)

@router.post("/refresh-token", response_model=RefreshTokenResponse)
def refresh_token(payload: RefreshTokenRequest, service: TokenServiceDep):
    """
    Endpoint for refresh token.
    """
    try:
        return service.refresh_token(payload.refresh_token)
    except InvalidRefreshTokenError as e:
        raise HTTPException(status_code=401, detail=str(e))
    
@router.get("/me", response_model=MeResponse)
def me(token: OAuthDep, service: AuthServiceDep):
    """
    Endpoint from player recognition
    """
    try:
        return service.get_player_from_token(token)
    except InvalidToken as e:
        raise HTTPException(status_code=401, detail=str(e))