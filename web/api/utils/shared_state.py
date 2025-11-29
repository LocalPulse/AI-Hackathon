import threading
import time
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ActiveTrack:
    """Active track in current frame."""
    track_id: int
    class_name: str
    activity: str
    confidence: float
    last_seen: float  # timestamp


class SharedState:
    
    def __init__(self, timeout: float = 5.0):
        """
        Initialize shared state.
        
        Args:
            timeout: Time in seconds after which a track is considered inactive
                    (increased to 5 seconds to account for video processing delays)
        """
        self._tracks: Dict[str, Dict[int, ActiveTrack]] = {}  # camera_id -> {track_id -> ActiveTrack}
        self._lock = threading.Lock()
        self._timeout = timeout
    
    def update_tracks(self, tracks: List[Dict], camera_id: Optional[str] = None):
        """
        Update active tracks from pipeline.
        
        Args:
            tracks: List of track dictionaries with keys: track_id, class_name, activity, confidence
            camera_id: Optional camera identifier
        """
        camera_id = camera_id or 'default'
        current_time = time.time()
        
        with self._lock:
            if camera_id not in self._tracks:
                self._tracks[camera_id] = {}
            self._update_active_tracks(tracks, camera_id, current_time)
            self._cleanup_old_tracks(camera_id, current_time)
    
    def _update_active_tracks(self, tracks: List[Dict], camera_id: str, current_time: float):
        """Update existing tracks and add new ones."""
        for track in tracks:
            track_id = track.get('track_id')
            if track_id is None:
                continue
            
            self._tracks[camera_id][track_id] = ActiveTrack(
                track_id=track_id,
                class_name=track.get('class_name', 'unknown'),
                activity=track.get('activity', 'unknown'),
                confidence=track.get('confidence', 0.0),
                last_seen=current_time
            )
    
    def _cleanup_old_tracks(self, camera_id: str, current_time: float):
        """Remove tracks that haven't been seen recently."""
        if camera_id not in self._tracks:
            return
        
        expired_ids = [
            track_id
            for track_id, track in self._tracks[camera_id].items()
            if current_time - track.last_seen > self._timeout
        ]
        
        for track_id in expired_ids:
            del self._tracks[camera_id][track_id]
        
        if not self._tracks[camera_id]:
            del self._tracks[camera_id]
    
    def get_active_tracks(self, camera_id: Optional[str] = None) -> List[ActiveTrack]:
        """Get list of currently active tracks."""
        with self._lock:
            if camera_id:
                if camera_id not in self._tracks:
                    return []
                return list(self._tracks[camera_id].values())
            
            all_tracks = []
            for camera_tracks in self._tracks.values():
                all_tracks.extend(camera_tracks.values())
            return all_tracks
    
    def get_stats(self, camera_id: Optional[str] = None) -> Dict[str, int]:
        """
        Get statistics about active tracks.
        
        Args:
            camera_id: Optional camera ID to filter by. If None, returns aggregated stats.
        
        Returns:
            Dictionary with counts by class: {'person': 5, 'train': 2, 'total': 7}
        """
        with self._lock:
            if camera_id:
                return self._get_camera_stats(camera_id)
            return self._get_all_stats()
    
    def _get_camera_stats(self, camera_id: str) -> Dict[str, int]:
        """Get statistics for a specific camera."""
        if camera_id not in self._tracks:
            return {'person': 0, 'train': 0, 'total': 0}
        
        stats = {}
        for track in self._tracks[camera_id].values():
            class_name = track.class_name
            stats[class_name] = stats.get(class_name, 0) + 1
        stats['total'] = len(self._tracks[camera_id])
        return stats
    
    def _get_all_stats(self) -> Dict[str, int]:
        """Get aggregated statistics across all cameras."""
        stats = {}
        total = 0
        for camera_tracks in self._tracks.values():
            for track in camera_tracks.values():
                class_name = track.class_name
                stats[class_name] = stats.get(class_name, 0) + 1
                total += 1
        stats['total'] = total
        return stats
    
    def get_person_count(self, camera_id: Optional[str] = None) -> int:
        """Get count of active person tracks."""
        with self._lock:
            return self._count_by_class('person', camera_id)
    
    def get_train_count(self, camera_id: Optional[str] = None) -> int:
        """Get count of active train tracks."""
        with self._lock:
            return self._count_by_class('train', camera_id)
    
    def _count_by_class(self, class_name: str, camera_id: Optional[str] = None) -> int:
        """Count tracks by class name."""
        if camera_id:
            if camera_id not in self._tracks:
                return 0
            return sum(1 for track in self._tracks[camera_id].values() if track.class_name == class_name)
        
        return sum(
            1
            for camera_tracks in self._tracks.values()
            for track in camera_tracks.values()
            if track.class_name == class_name
        )
    
    def get_camera_ids(self) -> List[str]:
        """Get list of active camera IDs."""
        with self._lock:
            return list(self._tracks.keys())
    
    def clear(self):
        """Clear all active tracks."""
        with self._lock:
            self._tracks.clear()


# Global shared state instance
_shared_state = SharedState()


def get_shared_state() -> SharedState:
    """Get the global shared state instance."""
    return _shared_state
