from uuid import uuid4

from app.repositories.player_repository import PlayerRepository
from app.core.exceptions.auth import  InvalidRegistration

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
            self.repo.update_last_login(player.id)
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
        
        return self.repo.create_user(email, name, password)
    
    def get_player_by_id(self, player_id: str):
        """
        Gets players by player_id
        """
        return self.repo.get_by_id(player_id)

    def generate_guest_name(self):
        """
        Generates a random guest name using a UUID.
        """
        return f"guest-{uuid4().hex[:6]}"