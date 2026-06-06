from fastapi import FastAPI
from app.core.config import settings
from app.api.v0.routes import health

app = FastAPI(title="OAuth service")

app.include_router(health.router, prefix="/v0")

@app.get("/")
def root():
    """
    Root endpoint for the OAuth service.
    """
    return {"status": "ok", "service": "OAuth", "env": settings.ENV}