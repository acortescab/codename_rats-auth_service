from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.db.models.player import Player


class PlayerRepository:
    """
    Repository class for managing player data in the database. 
    This class provides methods for retrieving and creating player records, 
    as well as updating player information such as the last login timestamp.
    """
    
    def __init__(self, write_db: Session, read_db: Session):
        """
        Initializes the PlayerRepository with separate read and write database sessions.
        """
        self.write_db = write_db
        self.read_db = read_db

    def get_by_device_id(self, device_id: str):
        """
        Retrieves a player by their device ID.
        """
        return self.read_db.query(Player).filter(
            Player.device_id == device_id
        ).first()

    def get_by_id(self, player_id):
        """
        Retrieves a player by their ID.
        """
        return self.read_db.query(Player).filter(
            Player.id == player_id
        ).first()

    def create(self, device_id: str, name: str):
        """
        Creates a new player.
        """
        player = Player(
            device_id=device_id,
            name=name
        )
        self.write_db.add(player)
        self.write_db.commit()
        self.write_db.refresh(player)
        return player

    def update_last_login(self, id):
        """
        Updates the last login timestamp for a player.
        """
        player = self.write_db.query(Player).filter(
            Player.id == id
        ).first()

        player.last_login = datetime.now(timezone.utc)
        self.write_db.commit()