from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    """
    Application settings for the OAuth service. 
    This class uses Pydantic's BaseSettings to load configuration 
    from environment variables or a .env file.
    Attributes:
        DATABASE_URL (str | None): The database connection URL. Required for the application to function.
        ENV (str): The application environment (e.g., "dev", "prod", "test"). Defaults to "dev".
    """
    model_config = ConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str | None = None
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
    Retrieves the application settings. This function is cached to ensure that the settings are only loaded once during the application's lifetime.
    Returns: Settings: The application settings.
    """
    return Settings()