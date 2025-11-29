"""
FastAPI application for YOLO detection monitoring.
Provides REST API endpoints for accessing detection logs and statistics.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.data_base import get_detections, get_detection_count
from src.utils.shared_state import get_shared_state

app = FastAPI(
    title="YOLO Detection Monitoring API",
    version="1.0.0",
    description="Real-time monitoring of YOLO object detection and activity tracking"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class Detection(BaseModel):
    """Detection log entry."""
    id: int
    track_id: int
    class_name: str
    activity: str
    confidence: float
    timestamp: str
    
    class Config:
        # Allow field alias for 'class' -> 'class_name'
        populate_by_name = True


class DetectionResponse(BaseModel):
    """Response for detection list endpoint."""
    total: int
    limit: int
    offset: int
    detections: List[Detection]


class CurrentStats(BaseModel):
    """Current statistics of active tracks."""
    person_count: int
    train_count: int
    total_tracks: int
    timestamp: str


# Endpoints

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "YOLO Detection Monitoring API",
        "version": "1.0.0",
        "endpoints": {
            "detections": "/detections",
            "stats": "/stats/current",
            "docs": "/docs"
        }
    }


@app.get("/detections", response_model=DetectionResponse)
async def get_detection_logs(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    class_filter: Optional[str] = Query(None, description="Filter by class (person, train)"),
    activity_filter: Optional[str] = Query(None, description="Filter by activity (standing, moving, stopped)")
):
    """
    Get detection logs from database.
    
    - **limit**: Maximum number of records to return (1-1000)
    - **offset**: Number of records to skip (for pagination)
    - **class_filter**: Filter by object class (person, train)
    - **activity_filter**: Filter by activity (standing, moving, stopped)
    """
    try:
        detections = get_detections(
            limit=limit,
            offset=offset,
            class_filter=class_filter,
            activity_filter=activity_filter
        )
        
        total = get_detection_count(
            class_filter=class_filter,
            activity_filter=activity_filter
        )
        
        # Convert 'class' field to 'class_name' for Pydantic model
        formatted_detections = [
            {
                "id": d["id"],
                "track_id": d["track_id"],
                "class_name": d["class"],
                "activity": d["activity"],
                "confidence": d["confidence"],
                "timestamp": d["timestamp"]
            }
            for d in detections
        ]
        
        return DetectionResponse(
            total=total,
            limit=limit,
            offset=offset,
            detections=formatted_detections
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/stats/current", response_model=CurrentStats)
async def get_current_stats():
    """
    Get statistics of currently active tracks in the video frame.
    
    Returns counts of person and train objects currently being tracked.
    """
    try:
        from datetime import datetime
        
        shared_state = get_shared_state()
        stats = shared_state.get_stats()
        
        return CurrentStats(
            person_count=stats.get('person', 0),
            train_count=stats.get('train', 0),
            total_tracks=stats.get('total', 0),
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
