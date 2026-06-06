from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str
    ENV: str = "dev"

    @property
    def is_prod(self):
        return self.ENV == "prod"
    
    @property
    def is_test(self):
        return self.ENV == "test"

settings = Settings()