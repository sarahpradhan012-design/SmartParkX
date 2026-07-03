from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def root():
    return {
        "message": "Welcome to SmartParkX",
        "status": "API is running successfully!"
    }


@router.get("/health")
def health_check():
    return {
        "status": "healthy"
    }