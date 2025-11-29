from typing import List, Dict, Optional
from web.streamlit.services.data_service import get_data_service, CameraData

class CameraManager:
    def __init__(self):
        self._data_service = get_data_service()
    
    def get_all_cameras(self) -> List[CameraData]:
        return self._data_service.get_cameras()
    
    def get_camera(self, camera_id: str) -> Optional[CameraData]:
        return self._data_service.get_camera(camera_id)
    
    def get_camera_stats(self, camera_id: str) -> Dict[str, int]:
        return self._data_service.get_camera_stats(camera_id)
    
    def get_all_cameras_stats(self) -> Dict[str, Dict[str, int]]:
        cameras = self.get_all_cameras()
        stats = {}
        for camera in cameras:
            stats[camera.camera_id] = self.get_camera_stats(camera.camera_id)
        return stats
    
    def get_aggregate_stats(self) -> Dict[str, int]:
        all_stats = self.get_all_cameras_stats()
        total_people = sum(stats.get("people", 0) for stats in all_stats.values())
        total_trains = sum(stats.get("trains", 0) for stats in all_stats.values())
        total_objects = sum(stats.get("total", 0) for stats in all_stats.values())
        
        return {
            "people": total_people,
            "trains": total_trains,
            "total": total_objects,
            "active_cameras": len([cam for cam in self.get_all_cameras() if cam.status == "active"])
        }

_instance: Optional[CameraManager] = None

def get_camera_manager() -> CameraManager:
    global _instance
    if _instance is None:
        _instance = CameraManager()
    return _instance

