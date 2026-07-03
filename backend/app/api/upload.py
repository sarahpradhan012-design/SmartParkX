from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.video_service import save_uploaded_video
from app.core.logger import logger

router = APIRouter()


@router.post("/upload")
def upload_video(file: UploadFile = File(...)):
    try:
        saved_path = save_uploaded_video(file)

        return {
            "message": "Video uploaded successfully",
            "filename": file.filename,
            "saved_path": saved_path
        }

    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))