import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, DateTime
from datetime import datetime, timezone

from app.db.base import Base

class Player(Base):
    """
    SQLAlchemy model for the players table.
    """
    __tablename__ = "players"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id = Column(String, unique=True, nullable=False)

    name = Column(String, nullable=False)
    
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    last_login = Column(DateTime, default=datetime.now(timezone.utc))