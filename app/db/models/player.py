import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base

from enum import Enum


class PlayerAccountType(str, Enum):
    """
    Enum for Encryptation algorithm
    """
    Guest = "guest"
    Registered = "registered"


class Player(Base):
    """
    SQLAlchemy model for the players table.
    """
    __tablename__ = "players"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id = Column(String, unique=True, nullable=False)
    
    email = Column(String, unique=True, index=True, nullable=True)
    password = Column(String, nullable=True)

    name = Column(String, nullable=False)
    account_type = Column(String)
    
    created_at = Column(DateTime, default=lambda:datetime.now(timezone.utc))
    last_login = Column(DateTime, default=lambda:datetime.now(timezone.utc))