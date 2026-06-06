import sys
from fastapi import FastAPI
from app.core.config import get_settings
from app.api.v0.routes import health
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting application...")

    try:
        validate_settings(get_settings())
    except RuntimeError as e:
        print(f"Error validating settings: {e}")
        sys.exit(1)
        
    yield 
    print("Closing application resources...")

app = FastAPI(lifespan=lifespan)

def validate_settings(settings):
    """
    Validates the application settings. Raises a RuntimeError if any required settings are missing or invalid.
    Args: settings (Settings): The application settings to validate.
    """
    if not settings.DATABASE_URL:
        raise RuntimeError("DATABASE_URL missing")

app.include_router(health.router, prefix="/v0")

@app.get("/")
def root():
    """
    Root endpoint for the OAuth service.
    """
    settings = get_settings()
    return {"status": "ok", "service": "OAuth", "env": settings.ENV}