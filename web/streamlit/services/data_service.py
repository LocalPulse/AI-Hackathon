from typing import List, Dict, Optional
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from web.api.utils.database import get_logs as db_get_logs, get_log_count as db_get_log_count

class CameraData:
    def __init__(self, camera_id: str, name: str, status: str):
        self.camera_id = camera_id
        self.name = name
        self.status = status

class LogEntry:
    def __init__(self, log_id: int, track_id: int, class_name: str, 
                 activity: str, confidence: float, timestamp: str, camera_id: Optional[str] = None):
        self.id = log_id
        self.track_id = track_id
        self.class_name = class_name
        self.activity = activity
        self.confidence = confidence
        self.timestamp = timestamp
        self.camera_id = camera_id

class DataService:
    def __init__(self):
        # Keep mock cameras for now (database doesn't have camera_id field)
        self._mock_cameras = self._generate_mock_cameras()
    
    def _generate_mock_cameras(self) -> List[CameraData]:
        return [
            CameraData("cam_001", "Platform 1 - North", "active"),
            CameraData("cam_002", "Platform 2 - South", "active"),
            CameraData("cam_003", "Platform 3 - East", "inactive"),
        ]
    
    def get_cameras(self) -> List[CameraData]:
        return self._mock_cameras
    
    def get_camera(self, camera_id: str) -> Optional[CameraData]:
        for cam in self._mock_cameras:
            if cam.camera_id == camera_id:
                return cam
        return None
    
    def get_camera_stats(self, camera_id: str) -> Dict[str, int]:
        # Use real database data
        logs = self.get_logs(limit=20)
        
        people_count = len([log for log in logs if log.class_name == "person"])
        train_count = len([log for log in logs if log.class_name == "train"])
        
        return {
            "people": people_count,
            "trains": train_count,
            "total": len(logs)
        }
    
    def get_logs(self, limit: int = 100, offset: int = 0, 
                 class_filter: Optional[str] = None,
                 activity_filter: Optional[str] = None,
                 camera_id: Optional[str] = None) -> List[LogEntry]:
        """Get logs from real database."""
        # Get logs from database
        db_logs = db_get_logs(
            limit=limit,
            offset=offset,
            class_filter=class_filter,
            activity_filter=activity_filter
        )
        
        # Convert database format to LogEntry objects
        log_entries = []
        for log in db_logs:
            log_entries.append(LogEntry(
                log_id=log["id"],
                track_id=log["track_id"],
                class_name=log["class"],
                activity=log["activity"],
                confidence=log["confidence"],
                timestamp=log["timestamp"],
                camera_id=None  # Database doesn't have camera_id yet
            ))
        
        return log_entries
    
    def get_log_count(self, class_filter: Optional[str] = None,
                     activity_filter: Optional[str] = None,
                     camera_id: Optional[str] = None) -> int:
        """Get log count from real database."""
        return db_get_log_count(
            class_filter=class_filter,
            activity_filter=activity_filter
        )
    
    def get_metrics_data(self, camera_id: Optional[str] = None) -> Dict:
        """Get metrics from real database logs."""
        logs = self.get_logs(limit=1000)
        
        if not logs:
            return {
                "average_confidence": 0.0,
                "fps": 0.0,
                "activity_distribution": {"standing": 0, "moving": 0, "stopped": 0},
                "detections_over_time": [],
                "track_duration": 0.0,
                "unique_objects": 0
            }
        
        confidences = [log.confidence for log in logs]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        activity_dist = {"standing": 0, "moving": 0, "stopped": 0}
        for log in logs:
            if log.activity in activity_dist:
                activity_dist[log.activity] += 1
        
        unique_tracks = len(set(log.track_id for log in logs))
        
        # Group by hour for time distribution
        time_data = []
        hour_counts = {}
        for log in logs:
            try:
                hour = int(log.timestamp.split()[1].split(":")[0])
                hour_counts[hour] = hour_counts.get(hour, 0) + 1
            except:
                pass
        
        for i in range(24):
            time_data.append({"hour": i, "count": hour_counts.get(i, 0)})
        
        return {
            "average_confidence": round(avg_confidence, 3),
            "fps": 25.0,  # Default FPS from config
            "activity_distribution": activity_dist,
            "detections_over_time": time_data,
            "track_duration": 0.0,  # Not available in current database
            "unique_objects": unique_tracks
        }

_instance: Optional[DataService] = None

def get_data_service() -> DataService:
    global _instance
    if _instance is None:
        _instance = DataService()
    return _instance

