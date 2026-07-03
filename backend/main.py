from fastapi import FastAPI

from app.api import health, upload, process

app = FastAPI(
    title="SmartParkX API",
    version="1.0.0",
    description="AI-Powered Parking Video Analytics Platform"
)

app.include_router(health.router)
app.include_router(upload.router)
app.include_router(process.router)