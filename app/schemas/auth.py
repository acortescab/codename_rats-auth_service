from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, EmailStr, Field, field_validator


# guest login schemas
class GuestLoginRequest(BaseModel):
    """
    Request model for guest login endpoint.
    """
    device_id: str

class GuestLoginResponse(BaseModel):
    """
    Response model for guest login.
    """
    id: UUID = Field(default_factory=uuid4)
    name: str
    access_token: str
    refresh_token: str


# Refresh token schemas
class RefreshTokenRequest(BaseModel):
    """
    Request model for refresh token endpoint
    """
    refresh_token: str

class RefreshTokenResponse(BaseModel):
    """
    Response model for refresh token
    """
    access_token: str
    refresh_token: str

# Me schemas
class MeResponse(BaseModel):
    """
    Response for player validation
    """
    id: UUID = Field(default_factory=uuid4)
    name: str
    email: str | None = None
    account_type: str

# Register schemas
class RegisterRequest(BaseModel):
    """
    Request for register
    """
    email: EmailStr
    name: str
    password: str = Field(
        min_length=8, 
        max_length=128
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if not any(c.isalpha() for c in v):
            raise ValueError("Password must contain at least one letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        return v

class RegisterResponse(BaseModel):
    """
    Response for register
    """
    id: UUID = Field(default_factory=uuid4)
    email: str
    name: str
    created_at: datetime

# Login schemas
class LoginRequest(BaseModel):
    """
    Request for login
    """
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    """
    Response model for login.
    """
    id: UUID = Field(default_factory=uuid4)
    name: str
    email: str
    access_token: str
    refresh_token: str