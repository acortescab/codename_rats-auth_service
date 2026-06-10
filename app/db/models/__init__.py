
def load_models():
    """
    Import models for alembic migrations
    """
    from app.db.models.player import Player
    from app.db.models.refresh_token import RefreshToken