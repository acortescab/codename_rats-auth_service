import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class RefreshToken(Base):
    """
    SQLAlchemy model for the refresh tokens table.
    """
    __tablename__ = "refresh_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    player_id = Column(UUID(as_uuid=True), ForeignKey("players.id"), nullable=False)
    jti = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    token_hash = Column(String, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda:datetime.now(timezone.utc))