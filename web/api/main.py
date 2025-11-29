import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Literal

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from web.api.utils.database import get_logs, get_log_count, get_active_camera_ids
from web.api.utils.shared_state import get_shared_state
from web.api.utils.state_sync import (
    get_running_camera_ids,
    get_camera_stats as get_sync_stats
)

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger(__name__)

API_NAME = "YOLO Detection Monitoring API"
API_VERSION = "1.0.0"
DEFAULT_LIMIT = 100
MAX_LIMIT = 1000
CAMERA_NOT_FOUND_THRESHOLD = 300  # seconds
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"

app = FastAPI(
    title=API_NAME,
    version=API_VERSION,
    description="Real-time monitoring of YOLO object detection and activity tracking"
)

ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:80",
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["X-Total-Count"],
)

# Pydantic models
class Detection(BaseModel):
    """Detection log entry."""
    id: int = Field(..., description="Unique detection ID")
    track_id: int = Field(..., ge=0, description="Track ID")
    class_name: Literal["person", "train"] = Field(..., description="Object class")
    activity: Literal["standing", "moving", "stopped"] = Field(..., description="Activity state")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    timestamp: str = Field(..., description="Detection timestamp")
    camera_id: Optional[str] = Field(None, description="Camera ID (for future use)")
    
    model_config = ConfigDict(populate_by_name=True)


class DetectionResponse(BaseModel):
    """Response for detection list endpoint."""
    total: int
    limit: int
    offset: int
    detections: List[Detection]


class CurrentStats(BaseModel):
    """Current statistics of active tracks."""
    person_count: int = Field(..., ge=0, description="Number of detected persons")
    train_count: int = Field(..., ge=0, description="Number of detected trains")
    total_tracks: int = Field(..., ge=0, description="Total number of tracks")
    timestamp: str = Field(..., description="Statistics timestamp")


class Camera(BaseModel):
    """Camera information."""
    id: str = Field(..., description="Camera ID")
    name: str = Field(..., min_length=1, description="Camera name")
    status: Literal["active", "inactive", "error"] = Field(..., description="Camera status")
    stats: CurrentStats = Field(..., description="Camera statistics")


class CameraListResponse(BaseModel):
    """Response for camera list endpoint."""
    cameras: List[Camera] = Field(..., description="List of cameras")
    total: int = Field(..., ge=0, description="Total number of cameras")


# Helper functions
def _get_current_timestamp() -> str:
    """Get current timestamp in standard format."""
    return datetime.now().strftime(TIMESTAMP_FORMAT)


def _create_current_stats(person: int, train: int, total: int) -> CurrentStats:
    """Create CurrentStats object."""
    return CurrentStats(
        person_count=person,
        train_count=train,
        total_tracks=total,
        timestamp=_get_current_timestamp()
    )


def _format_detection(log: Dict) -> Detection:
    """Format database log entry to Detection model."""
    return Detection(
        id=log["id"],
        track_id=log["track_id"],
        class_name=log["class"],
        activity=log["activity"],
        confidence=float(log["confidence"]),
        timestamp=log["timestamp"],
        camera_id=log.get("camera_id")
    )


def _format_camera_name(camera_id: str) -> str:
    """Format camera ID into display name."""
    return f"Camera {camera_id.replace('camera-', '').replace('default', 'Default')}"


def _create_camera_response(camera_id: str, sync_stats: Dict[str, int]) -> Camera:
    """Create Camera response object."""
    stats = _create_current_stats(
        person=sync_stats.get('person', 0),
        train=sync_stats.get('train', 0),
        total=sync_stats.get('total', 0)
    )
    
    return Camera(
        id=camera_id,
        name=_format_camera_name(camera_id),
        status="active",
        stats=stats
    )


def _check_camera_exists(camera_id: str, shared_state) -> bool:
    """Check if camera exists in database or sync state."""
    if camera_id in shared_state.get_camera_ids():
        return True
    
    db_camera_ids = get_active_camera_ids(seconds_threshold=CAMERA_NOT_FOUND_THRESHOLD)
    sync_camera_ids = get_running_camera_ids()
    
    return camera_id in db_camera_ids or camera_id in sync_camera_ids


def _handle_database_error(e: Exception, operation: str):
    """Handle database-related errors."""
    if isinstance(e, ValueError):
        logger.error(f"Validation error in {operation}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request parameters: {str(e)}"
        )
    
    logger.error(f"Database error in {operation}: {e}", exc_info=True)
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Internal server error while {operation}"
    )


def _handle_general_error(e: Exception, operation: str):
    """Handle general errors."""
    logger.error(f"Error in {operation}: {e}", exc_info=True)
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Internal server error while {operation}"
    )


# Endpoints
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": API_NAME,
        "version": API_VERSION,
        "endpoints": {
            "detections": "/detections",
            "stats": "/stats/current",
            "docs": "/docs"
        }
    }


@app.get("/detections", response_model=DetectionResponse)
async def get_detection_logs(
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT, description="Maximum number of records"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    class_filter: Optional[Literal["person", "train"]] = Query(
        None, 
        description="Filter by class (person, train)"
    ),
    activity_filter: Optional[Literal["standing", "moving", "stopped"]] = Query(
        None, 
        description="Filter by activity (standing, moving, stopped)"
    ),
    camera_id: Optional[str] = Query(None, description="Filter by camera ID (for future use)")
):
    """
    Get detection logs from database.
    
    - **limit**: Maximum number of records to return (1-1000)
    - **offset**: Number of records to skip (for pagination)
    - **class_filter**: Filter by object class (person, train)
    - **activity_filter**: Filter by activity (standing, moving, stopped)
    - **camera_id**: Filter by camera ID (for future use)
    """
    try:
        logs = get_logs(
            limit=limit,
            offset=offset,
            class_filter=class_filter,
            activity_filter=activity_filter,
            camera_id=camera_id
        )
        
        total = get_log_count(
            class_filter=class_filter,
            activity_filter=activity_filter,
            camera_id=camera_id
        )
        
        formatted_detections = [_format_detection(log) for log in logs]
        
        response = DetectionResponse(
            total=total,
            limit=limit,
            offset=offset,
            detections=formatted_detections
        )
        
        return JSONResponse(
            content=response.model_dump(),
            headers={"X-Total-Count": str(total)}
        )
    except HTTPException:
        raise
    except Exception as e:
        _handle_database_error(e, "fetching logs")


@app.get("/stats/current", response_model=CurrentStats)
async def get_current_stats():
    """
    Get statistics of currently active tracks in the video frame.
    
    Returns counts of person and train objects currently being tracked.
    """
    try:
        shared_state = get_shared_state()
        stats = shared_state.get_stats()
        
        return _create_current_stats(
            person=stats.get('person', 0),
            train=stats.get('train', 0),
            total=stats.get('total', 0)
        )
    except Exception as e:
        _handle_general_error(e, "fetching statistics")


@app.get("/cameras", response_model=CameraListResponse)
async def get_cameras():
    """
    Get list of all cameras with their current statistics.
    
    Returns cameras from shared state (real-time active tracks in current frame).
    Uses file-based sync for multiprocessing support.
    """
    try:
        running_camera_ids = get_running_camera_ids()
        cameras = [
            _create_camera_response(camera_id, get_sync_stats(camera_id))
            for camera_id in sorted(running_camera_ids)
        ]
        
        return CameraListResponse(cameras=cameras, total=len(cameras))
    except Exception as e:
        _handle_general_error(e, "fetching cameras")


@app.get("/cameras/{camera_id}/stats", response_model=CurrentStats)
async def get_camera_stats(camera_id: str):
    """
    Get statistics for a specific camera.
    
    Returns real-time statistics from shared state (current active tracks in frame).
    Uses file-based sync for multiprocessing support.
    
    Args:
        camera_id: Camera identifier
    """
    try:
        shared_state = get_shared_state()
        shared_stats = shared_state.get_stats(camera_id=camera_id)
        sync_stats = get_sync_stats(camera_id)
        
        person_count = max(shared_stats.get('person', 0), sync_stats.get('person', 0))
        train_count = max(shared_stats.get('train', 0), sync_stats.get('train', 0))
        total_tracks = max(shared_stats.get('total', 0), sync_stats.get('total', 0))
        
        if not _should_check_camera_exists(total_tracks, camera_id, shared_state):
            return _create_current_stats(person_count, train_count, total_tracks)
        
        if not _check_camera_exists(camera_id, shared_state):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Camera {camera_id} not found"
            )
        
        return _create_current_stats(person_count, train_count, total_tracks)
    except HTTPException:
        raise
    except Exception as e:
        _handle_general_error(e, "fetching camera statistics")


def _should_check_camera_exists(total_tracks: int, camera_id: str, shared_state) -> bool:
    """Check if we need to verify camera existence."""
    if total_tracks > 0:
        return False
    return camera_id not in shared_state.get_camera_ids()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        get_log_count()
        return {
            "status": "healthy",
            "database": "connected",
            "service": API_NAME
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unhealthy: {str(e)}"
        )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Custom exception handler for better error responses."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "status_code": 500
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
