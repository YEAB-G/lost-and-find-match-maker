from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check():
    """Health check endpoint to verify the backend is running."""
    return {
        "status": "healthy",
        "service": "University Lost & Found Matcher",
        "version": "0.1.0",
    }
