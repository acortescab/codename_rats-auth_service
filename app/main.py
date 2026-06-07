import sys
import os
from fastapi import FastAPI
from app.core.config import get_settings
from app.api.v0.routes import health, auth
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan function to manage application startup and shutdown events.
    """
    print("Starting application...")

    try:
        validate_settings(get_settings())
    except RuntimeError as e:
        print(f"Error validating settings: {e}")
        sys.exit(1)
        
    yield 
    print("Closing application resources...")

def validate_settings(settings):
    """
    Validates the application settings. Raises a RuntimeError if any required settings are missing or invalid.
    Args: settings (Settings): The application settings to validate.
    """
    if not settings.SECRET_KEY:
        raise RuntimeError("SECRET KEY IS NULL")
    if not os.getenv("DATABASE_URL_READER"):
        raise RuntimeError("DATABASE_URL_READER missing")
    if not os.getenv("DATABASE_URL_WRITER"):
        raise RuntimeError("DATABASE_URL_WRITER missing")
    
app = FastAPI(lifespan=lifespan)
app.include_router(health.router, prefix="/v0")
app.include_router(auth.router, prefix="/v0")

@app.get("/")
def root():
    """
    Root endpoint for the OAuth service.
    """
    settings = get_settings()
    return {"status": "ok", "service": "OAuth", "env": settings.ENV}
