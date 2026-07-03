import os
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import FileResponse

from app.services.video_service import process_video_with_yolo
from app.core.config import PROCESSED_DIR, REPORTS_DIR
from app.core.logger import logger


router = APIRouter()


@router.post("/process")
def process_video(filename: str = Query(...)):
    try:
        return process_video_with_yolo(filename)
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/video/{filename}")
def download_processed_video(filename: str):
    file_path = os.path.join(PROCESSED_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Processed video not found.")

    logger.info(f"Downloading processed video: {filename}")

    return FileResponse(
        path=file_path,
        media_type="video/mp4",
        filename=filename
    )


@router.get("/download/report/{filename}")
def download_detection_report(filename: str):
    file_path = os.path.join(REPORTS_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Detection report not found.")

    logger.info(f"Downloading detection report: {filename}")

    return FileResponse(
        path=file_path,
        media_type="application/json",
        filename=filename
    )