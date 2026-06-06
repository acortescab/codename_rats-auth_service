from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/")
def health_check():
    """
    Health check endpoint for the OAuth service.
    """
    return {"status": "ok", "version": "v0"}