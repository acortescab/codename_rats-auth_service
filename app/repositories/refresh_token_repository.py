import hashlib
from datetime import datetime

from sqlalchemy.orm import Session

from app.db.models.refresh_token import RefreshToken


class RefreshTokenRepository:
    """
    Repository for managing refresh tokens.
    """
    def __init__(self, write_db: Session, read_db: Session):
        """
        Initializes the RefreshTokenRepository with separate read and write database sessions.
        """
        self.write_db = write_db
        self.read_db = read_db

    def create(self, player_id, jti, token, expires_at: datetime):
        """
        Creates a new refresh token
        """
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        db_token = RefreshToken(
            player_id=player_id,
            jti=jti,
            token_hash=token_hash,
            revoked=False,
            expires_at=expires_at,
        )

        self.write_db.add(db_token)
        self.write_db.commit()
        return db_token
    
    def update(self, obj):
        """
        Update registries
        """
        self.write_db.add(obj)
        self.write_db.commit()
    
    def get_by_player_id(self, player_id):
        """
        Gets a token by player id
        """
        return self.read_db.query(RefreshToken).filter(
            player_id == player_id
        ).first()
    
    def get_by_jti(self, jti):
        """
        Gets a token by jti
        """
        return self.read_db.query(RefreshToken).filter(
            RefreshToken.jti == jti,
            not RefreshToken.revoked
        ).first()

