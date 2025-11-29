from typing import Dict, List, Optional
from web.streamlit.services.data_service import get_data_service

class MetricsCalculator:
    def __init__(self):
        self._data_service = get_data_service()
    
    def calculate_metrics(self, camera_id: Optional[str] = None) -> Dict:
        raw_data = self._data_service.get_metrics_data(camera_id)
        
        return {
            "average_confidence": raw_data["average_confidence"],
            "fps": raw_data["fps"],
            "activity_distribution": raw_data["activity_distribution"],
            "detections_over_time": raw_data["detections_over_time"],
            "track_duration": raw_data["track_duration"],
            "unique_objects": raw_data["unique_objects"],
            "total_detections": len(self._data_service.get_logs(camera_id=camera_id)),
            "detection_rate": self._calculate_detection_rate(camera_id),
        }
    
    def _calculate_detection_rate(self, camera_id: Optional[str] = None) -> float:
        logs = self._data_service.get_logs(limit=1000, camera_id=camera_id)
        if not logs:
            return 0.0
        
        time_span = self._get_time_span(logs)
        if time_span == 0:
            return 0.0
        
        return round(len(logs) / time_span * 60, 2)
    
    def _get_time_span(self, logs: List) -> float:
        if len(logs) < 2:
            return 1.0
        
        from datetime import datetime
        try:
            first_time = datetime.strptime(logs[-1].timestamp, "%Y-%m-%d %H:%M:%S")
            last_time = datetime.strptime(logs[0].timestamp, "%Y-%m-%d %H:%M:%S")
            diff = (last_time - first_time).total_seconds()
            return max(diff / 60.0, 1.0)
        except:
            return 1.0
    
    def get_activity_percentages(self, camera_id: Optional[str] = None) -> Dict[str, float]:
        metrics = self.calculate_metrics(camera_id)
        dist = metrics["activity_distribution"]
        total = sum(dist.values())
        
        if total == 0:
            return {"standing": 0.0, "moving": 0.0, "stopped": 0.0}
        
        return {
            "standing": round(dist["standing"] / total * 100, 1),
            "moving": round(dist["moving"] / total * 100, 1),
            "stopped": round(dist["stopped"] / total * 100, 1),
        }

_instance: Optional[MetricsCalculator] = None

def get_metrics_calculator() -> MetricsCalculator:
    global _instance
    if _instance is None:
        _instance = MetricsCalculator()
    return _instance

