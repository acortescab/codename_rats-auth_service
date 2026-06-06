from uuid import UUID, uuid4

from pydantic import BaseModel, Field

class GuestLoginRequest(BaseModel):
    """
    Request model for guest login endpoint.
    """
    device_id: str

class AuthResponse(BaseModel):
    """
    Response model for authentication endpoints, including guest login.
    """
    id: UUID = Field(default_factory=uuid4)
    name: str
    access_token: str
    refresh_token: str