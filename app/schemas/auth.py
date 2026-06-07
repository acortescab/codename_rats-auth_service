from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class GuestLoginRequest(BaseModel):
    """
    Request model for guest login endpoint.
    """
    device_id: str

class RefreshTokenRequest(BaseModel):
    """
    Request model for refresh token endpoint
    """
    refresh_token: str

class GuestLoginResponse(BaseModel):
    """
    Response model for guest login.
    """
    id: UUID = Field(default_factory=uuid4)
    name: str
    access_token: str
    refresh_token: str

class RefreshTokenResponse(BaseModel):
    """
    Response model for refresh token
    """
    access_token: str
    refresh_token: str

class MeResponse(BaseModel):
    """
    Response for player validation
    """
    id: UUID = Field(default_factory=uuid4)
    name: str
