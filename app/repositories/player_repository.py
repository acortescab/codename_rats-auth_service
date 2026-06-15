from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.models.player import Player, PlayerAccountType


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

    def create_guest(self, device_id: str, name: str):
        """
        Creates a new player guest.
        """
        player = Player(
            device_id=device_id,
            name=name,
            account_type=PlayerAccountType.Guest
        )

        self.write_db.add(player)
        self.write_db.commit()
        self.write_db.refresh(player)
        return player
    
    def create_user(self, email:str, name:str, password:str):
        """
        Creates a new user
        """
        player = Player(
            email=email,
            name=name,
            password=hash_password(password),
            account_type=PlayerAccountType.Registered
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

    def get_by_email(self, email:str):
        """
        Retrieves a player by their email
        """
        return self.read_db.query(Player).filter(
            Player.email == email
        ).first()
    
    def upgrade_guest(self, id, email:str, password:str, name: str):
        """
        Upgrades a guest account to registered account
        """
        player = self.write_db.query(Player).filter(
            Player.id == id
        ).first()

        player.device_id = None
        player.email = email
        player.password = hash_password(password)
        player.name = name
        player.account_type = PlayerAccountType.Registered

        self.write_db.commit()
        self.write_db.refresh(player)

        return player