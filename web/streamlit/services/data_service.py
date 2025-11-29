from typing import List, Dict, Optional
from datetime import datetime, timedelta
import random

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
        self._mock_cameras = self._generate_mock_cameras()
        self._mock_logs = self._generate_mock_logs()
    
    def _generate_mock_cameras(self) -> List[CameraData]:
        return [
            CameraData("cam_001", "Platform 1 - North", "active"),
            CameraData("cam_002", "Platform 2 - South", "active"),
            CameraData("cam_003", "Platform 3 - East", "inactive"),
        ]
    
    def _generate_mock_logs(self) -> List[LogEntry]:
        logs = []
        base_time = datetime.now()
        classes = ["person", "train"]
        activities = ["standing", "moving", "stopped"]
        
        for i in range(100):
            log_time = base_time - timedelta(minutes=random.randint(0, 60))
            logs.append(LogEntry(
                log_id=i + 1,
                track_id=random.randint(1, 50),
                class_name=random.choice(classes),
                activity=random.choice(activities),
                confidence=round(random.uniform(0.5, 0.99), 2),
                timestamp=log_time.strftime("%Y-%m-%d %H:%M:%S"),
                camera_id=random.choice(["cam_001", "cam_002", "cam_003"])
            ))
        
        return sorted(logs, key=lambda x: x.timestamp, reverse=True)
    
    def get_cameras(self) -> List[CameraData]:
        return self._mock_cameras
    
    def get_camera(self, camera_id: str) -> Optional[CameraData]:
        for cam in self._mock_cameras:
            if cam.camera_id == camera_id:
                return cam
        return None
    
    def get_camera_stats(self, camera_id: str) -> Dict[str, int]:
        camera_logs = [log for log in self._mock_logs if log.camera_id == camera_id]
        recent_logs = camera_logs[:20]
        
        people_count = len([log for log in recent_logs if log.class_name == "person"])
        train_count = len([log for log in recent_logs if log.class_name == "train"])
        
        return {
            "people": people_count,
            "trains": train_count,
            "total": len(recent_logs)
        }
    
    def get_logs(self, limit: int = 100, offset: int = 0, 
                 class_filter: Optional[str] = None,
                 activity_filter: Optional[str] = None,
                 camera_id: Optional[str] = None) -> List[LogEntry]:
        filtered = self._mock_logs
        
        if class_filter:
            filtered = [log for log in filtered if log.class_name == class_filter]
        if activity_filter:
            filtered = [log for log in filtered if log.activity == activity_filter]
        if camera_id:
            filtered = [log for log in filtered if log.camera_id == camera_id]
        
        return filtered[offset:offset + limit]
    
    def get_log_count(self, class_filter: Optional[str] = None,
                     activity_filter: Optional[str] = None,
                     camera_id: Optional[str] = None) -> int:
        filtered = self._mock_logs
        
        if class_filter:
            filtered = [log for log in filtered if log.class_name == class_filter]
        if activity_filter:
            filtered = [log for log in filtered if log.activity == activity_filter]
        if camera_id:
            filtered = [log for log in filtered if log.camera_id == camera_id]
        
        return len(filtered)
    
    def get_metrics_data(self, camera_id: Optional[str] = None) -> Dict:
        logs = self._mock_logs
        if camera_id:
            logs = [log for log in logs if log.camera_id == camera_id]
        
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
        
        time_data = []
        for i in range(24):
            hour_logs = [log for log in logs if int(log.timestamp.split()[1].split(":")[0]) == i]
            time_data.append({"hour": i, "count": len(hour_logs)})
        
        return {
            "average_confidence": round(avg_confidence, 3),
            "fps": round(random.uniform(20, 30), 1),
            "activity_distribution": activity_dist,
            "detections_over_time": time_data,
            "track_duration": round(random.uniform(5, 15), 1),
            "unique_objects": unique_tracks
        }

_instance: Optional[DataService] = None

def get_data_service() -> DataService:
    global _instance
    if _instance is None:
        _instance = DataService()
    return _instance

