import os
import shutil
import cv2
import json
import time
from collections import Counter
from fastapi import UploadFile

from app.core.config import UPLOAD_DIR, PROCESSED_DIR, REPORTS_DIR
from app.core.logger import logger
from app.ai.detector import VehicleDetector


detector = VehicleDetector()

ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov"}


def save_uploaded_video(file: UploadFile) -> str:
    if not file.filename:
        raise ValueError("No file provided.")

    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension not in ALLOWED_VIDEO_EXTENSIONS:
        raise ValueError("Invalid file type. Allowed formats: .mp4, .avi, .mov")

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    logger.info(f"Saving uploaded video: {file.filename}")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    if os.path.getsize(file_path) == 0:
        os.remove(file_path)
        raise ValueError("Uploaded file is empty.")

    logger.info(f"Video saved successfully: {file_path}")

    return file_path


def process_video_with_yolo(filename: str):
    start_time = time.time()

    input_path = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(input_path):
        raise ValueError(f"Uploaded video not found: {filename}")

    logger.info(f"Starting YOLO processing for: {filename}")

    output_filename = f"annotated_{filename}"
    output_path = os.path.join(PROCESSED_DIR, output_filename)

    report_filename = f"detections_{os.path.splitext(filename)[0]}.json"
    report_path = os.path.join(REPORTS_DIR, report_filename)

    cap = cv2.VideoCapture(input_path)

    if not cap.isOpened():
        raise ValueError("Could not open uploaded video.")

    fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    writer = cv2.VideoWriter(
        output_path,
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height)
    )

    frame_count = 0
    total_detections = 0
    class_counter = Counter()
    detection_logs = []

    while True:
        success, frame = cap.read()

        if not success:
            break

        detections = detector.detect_frame(frame)

        for detection in detections:
            x1, y1, x2, y2 = detection["box"]
            class_name = detection["class_name"]
            confidence = detection["confidence"]

            label = f"{class_name} {confidence:.2f}"

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                frame,
                label,
                (x1, max(y1 - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

            detection_logs.append({
                "frame": frame_count,
                "class": class_name,
                "confidence": round(confidence, 4),
                "bbox": [x1, y1, x2, y2]
            })

            class_counter[class_name] += 1

        total_detections += len(detections)
        frame_count += 1
        writer.write(frame)

    cap.release()
    writer.release()

    processing_time = round(time.time() - start_time, 2)
    processing_fps = round(frame_count / processing_time, 2) if processing_time > 0 else 0

    report_data = {
        "input_video": filename,
        "output_video": output_filename,
        "frames_processed": frame_count,
        "total_vehicle_detections": total_detections,
        "detections_by_class": dict(class_counter),
        "processing_time_seconds": processing_time,
        "processing_fps": processing_fps,
        "detections": detection_logs
    }

    with open(report_path, "w") as report_file:
        json.dump(report_data, report_file, indent=4)

    logger.info(f"Processing completed for {filename} in {processing_time} seconds")

    return {
        "message": "Video processed successfully",
        "input_video": filename,
        "output_video": output_filename,
        "processed_path": output_path,
        "report_file": report_filename,
        "report_path": report_path,
        "frames_processed": frame_count,
        "total_vehicle_detections": total_detections,
        "detections_by_class": dict(class_counter),
        "processing_time_seconds": processing_time,
        "processing_fps": processing_fps
    }