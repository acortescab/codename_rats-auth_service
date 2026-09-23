from functools import lru_cache

from dotenv import load_dotenv
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

from app.core.security import JWTAlgorithm

# load .env file
load_dotenv()

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or .env file.
    """
    model_config = ConfigDict(env_file=".env", extra="ignore")

    SECRET_KEY: str
    ALGORITHM: JWTAlgorithm  = JWTAlgorithm.HS256
    ENV: str = "dev"

    @property
    def is_prod(self):
        """
        Checks if the application is running in the production environment.
        Returns: bool: True if the environment is "prod", False otherwise.
        """
        return self.ENV == "prod"

    @property
    def is_test(self):
        """
        Checks if the application is running in the test environment.
        Returns: bool: True if the environment is "test", False otherwise.
        """
        return self.ENV == "test"

@lru_cache
def get_settings():
    """
    Retrieves the application settings. 
    This function is cached to ensure that the settings are only loaded once during the application's lifetime.
    Returns: Settings: The application settings.
    """
    return Settings()
    