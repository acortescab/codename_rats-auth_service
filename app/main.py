import logging
import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v0.routes import auth, health
from app.core.config import get_settings

# Loggins configuration
logging.root.handlers = []

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logging.getLogger("uvicorn").setLevel(logging.INFO)
logging.getLogger("uvicorn.access").setLevel(logging.INFO)
logging.getLogger("uvicorn.error").setLevel(logging.INFO)

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
