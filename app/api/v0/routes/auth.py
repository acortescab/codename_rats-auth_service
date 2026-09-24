from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials

from app.core.exceptions.auth import InvalidCredentials, InvalidRegistration, InvalidToken
from app.core.rate_limit import limiter
from app.core.security import oauth2_scheme
from app.dependencies import get_auth_service, get_player_service, get_token_service
from app.schemas.auth import (
    GuestLoginRequest,
    GuestLoginResponse,
    LoginRequest,
    LoginResponse,
    MeResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    RegisterRequest,
    RegisterResponse,
)
from app.services.auth_service import AuthService, PlayerService, TokenService

# Authentication routes for the OAuth service
router = APIRouter(prefix="/auth", tags=["auth"])

# Resolve Dependency Injection to get multiple services
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
TokenServiceDep = Annotated[TokenService, Depends(get_token_service)]
PlayerServiceDep = Annotated[PlayerService, Depends(get_player_service)]

@router.post("/guest-login", response_model=GuestLoginResponse)
@limiter.limit("20/minute")
def guest_login(request: Request, payload: GuestLoginRequest, service: AuthServiceDep):
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
    except InvalidToken as e:
        raise HTTPException(status_code=401, detail=str(e))
    
@router.get("/me", response_model=MeResponse)
# Requires access token as a header
def me(token: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)], service: AuthServiceDep):
    """
    Endpoint for player recognition
    """
    try:
        return service.me(token.credentials)
    except InvalidToken as e:
        raise HTTPException(status_code=401, detail=str(e))
    
@router.post("/logout")
# Requires refresh token as a header
def logout(token: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)], service: AuthServiceDep):
    """
    Endpoint for player logout
    """
    try:
        return service.logout_player(token.credentials)
    except InvalidToken as e:
        raise HTTPException(status_code=401, detail=str(e))
    
@router.post("/register", response_model=RegisterResponse)
def register(payload: RegisterRequest, service: AuthServiceDep):
    """
    Endpoint for user register
    """
    try:
        return service.register_user(payload.email, payload.name, payload.password)
    except InvalidRegistration as e:
        raise HTTPException(status_code=409, detail=str(e))

@limiter.limit("20/minute")
@router.post("/login", response_model=LoginResponse)
def login(request: Request, payload: LoginRequest, service: AuthServiceDep):
    """
    Endpoint for login
    """
    try:
        return service.login(payload.email, payload.password)
    except InvalidCredentials as e:
        raise HTTPException(status_code=401, detail=str(e))
    
@router.post("/link-account", response_model=RegisterResponse)
def link_account(payload: RegisterRequest, token: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)], 
                 service: AuthServiceDep):
    """
    Endpoint for link account
    """
    try:
        return service.link_account(payload.email, payload.name, payload.password, token.credentials)
    except InvalidToken as e:
        raise HTTPException(status_code=401, detail=str(e))
    except InvalidRegistration as e:
        raise HTTPException(status_code=409, detail=str(e))