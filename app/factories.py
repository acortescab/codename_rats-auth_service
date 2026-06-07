from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.player_repository import PlayerRepository
from app.services.player_service import PlayerService
from app.services.auth_service import AuthService
from app.services.token_service import TokenService

def create_player_service(write_db, read_db):
    """
    Creates a PlayerService instance with a PlayerRepository.
    """
    repo = PlayerRepository(write_db, read_db)
    return PlayerService(repo)

def create_auth_service(write_db, read_db):
    """
    Creates an AuthService instance with a PlayerService and TokenService.
    """
    player_service = create_player_service(write_db, read_db)
    token_service = create_token_service(write_db, read_db)
    return AuthService(player_service, token_service)

def create_token_service(write_db, read_db):
    """
    Creates a TokenService instance.
    """
    repo = RefreshTokenRepository(write_db, read_db)
    return TokenService(repo)