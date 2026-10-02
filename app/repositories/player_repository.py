import logging
from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions.auth import InvalidCredentials, InvalidRegistration
from app.core.security import hash_password
from app.db.models.player import Player, PlayerAccountType

logger = logging.getLogger("__name__")

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

    def create_guest(self, device_id: str, name: str, device_secret_hash: str | None = None):
        """
        Creates a new player guest.
        """
        player = Player(
            device_id=device_id,
            device_secret_hash=device_secret_hash,
            name=name,
            account_type=PlayerAccountType.Guest
        )

        self.write_db.add(player)

        try:
            self.write_db.commit()
        except IntegrityError:
            # concurrent first login for the same device_id
            self.write_db.rollback()
            raise InvalidCredentials("Invalid device credentials")

        self.write_db.refresh(player)
        return player

    def set_device_secret_if_unset(self, player_id, device_secret_hash: str) -> bool:
        """
        Stores a device secret only if the player has none yet.
        The conditional UPDATE guarantees that exactly one concurrent claim wins.
        """
        rows = self.write_db.query(Player).filter(
            Player.id == player_id,
            Player.device_secret_hash.is_(None)
        ).update({"device_secret_hash": device_secret_hash})

        self.write_db.commit()
        return rows > 0
    
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
        self._commit_registration()
        self.write_db.refresh(player)
        return player

    def _commit_registration(self):
        """
        Commits a registration; a unique-constraint violation (e.g. a concurrent signup with the same
        email) becomes an InvalidRegistration (409) instead of an unhandled 500.
        """
        try:
            self.write_db.commit()
        except IntegrityError:
            self.write_db.rollback()
            raise InvalidRegistration("Invalid registration")

    def update_last_login(self, id):
        """
        Updates the last login timestamp for a player.
        """
        player = self.write_db.query(Player).filter(
            Player.id == id
        ).first()

        if player is None:
            return

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
        player.device_secret_hash = None
        player.email = email
        player.password = hash_password(password)
        player.name = name
        player.account_type = PlayerAccountType.Registered

        self._commit_registration()
        self.write_db.refresh(player)

        return player