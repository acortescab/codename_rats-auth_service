from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies import get_auth_service
from app.schemas.auth import GuestLoginRequest
from app.services.auth_service import AuthResponse, AuthService

# Authentication routes for the OAuth service
router = APIRouter(prefix="/auth", tags=["auth"])

# Resolve Dependency Injection to get auth service
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]

@router.post("/guest-login", response_model=AuthResponse)
def guest_login(payload: GuestLoginRequest, service: AuthServiceDep):
    """
    Endpoint for guest login. This is a placeholder implementation and should be replaced with actual authentication logic.
    """
    return service.guest_login(payload.device_id)