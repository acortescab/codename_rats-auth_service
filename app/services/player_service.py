from uuid import uuid4

from app.core.exceptions.auth import InvalidRegistration
from app.repositories.player_repository import PlayerRepository


class PlayerService:
    """
    Service class for managing player-related operations.
    """
    def __init__(self, repo: PlayerRepository):
        """
        Initializes the PlayerService with a PlayerRepository instance.
        """
        self.repo = repo
        
    def get_or_create_guest(self, device_id: str):
        """
        Gets an existing guest player or creates a new one if none exists.
        """
        player = self.repo.get_by_device_id(device_id)

        if player:
            self.update_last_login(player.id)
            return player

        name = self.generate_guest_name()

        return self.repo.create_guest(device_id=device_id, name=name)
    
    def register_user(self, email:str, password:str, name: str):
        """
        Register a new player
        """
        player = self.repo.get_by_email(email)

        if player:
            raise InvalidRegistration("Email is already in use")
        
        print(f"password is {password}")

        return self.repo.create_user(email, name, password)
    
    def get_player_by_id(self, player_id: str):
        """
        Gets player by player_id
        """
        return self.repo.get_by_id(player_id)
    
    def get_player_by_email(self, email: str):
        """
        Gets player by email
        """
        return self.repo.get_by_email(email)

    def generate_guest_name(self):
        """
        Generates a random guest name using a UUID.
        """
        return f"guest-{uuid4().hex[:6]}"
    
    def link_account(self, player_id: str, email:str, password:str, name: str):
        """
        Upgrade guest account to registered account
        """
        return self.repo.upgrade_guest(player_id, email, password, name)
    
    def update_last_login(self, player_id: str):
        """
        Updates last login by player_id
        """
        self.repo.update_last_login(player_id)
