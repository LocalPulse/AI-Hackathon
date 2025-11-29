"""
Shared state module for tracking active detections in real-time.
Thread-safe storage for current tracks visible in the video frame.
"""

import threading
import time
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class ActiveTrack:
    """Represents an active track in the current frame."""
    track_id: int
    class_name: str
    activity: str
    confidence: float
    last_seen: float  # timestamp


class SharedState:
    """Thread-safe storage for active tracks."""
    
    def __init__(self, timeout: float = 2.0):
        """
        Initialize shared state.
        
        Args:
            timeout: Time in seconds after which a track is considered inactive
        """
        self._tracks: Dict[int, ActiveTrack] = {}
        self._lock = threading.Lock()
        self._timeout = timeout
    
    def update_tracks(self, tracks: List[Dict]):
        """
        Update active tracks from pipeline.
        
        Args:
            tracks: List of track dictionaries with keys: track_id, class_name, activity, confidence
        """
        current_time = time.time()
        
        with self._lock:
            self._update_active_tracks(tracks, current_time)
            self._cleanup_old_tracks(current_time)
    
    def _update_active_tracks(self, tracks: List[Dict], current_time: float):
        """Update existing tracks and add new ones."""
        for track in tracks:
            track_id = track.get('track_id')
            if track_id is None:
                continue
            
            self._tracks[track_id] = ActiveTrack(
                track_id=track_id,
                class_name=track.get('class_name', 'unknown'),
                activity=track.get('activity', 'unknown'),
                confidence=track.get('confidence', 0.0),
                last_seen=current_time
            )
    
    def _cleanup_old_tracks(self, current_time: float):
        """Remove tracks that haven't been seen recently."""
        expired_ids = [
            track_id
            for track_id, track in self._tracks.items()
            if current_time - track.last_seen > self._timeout
        ]
        
        for track_id in expired_ids:
            del self._tracks[track_id]
    
    def get_active_tracks(self) -> List[ActiveTrack]:
        """Get list of currently active tracks."""
        with self._lock:
            return list(self._tracks.values())
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get statistics about active tracks.
        
        Returns:
            Dictionary with counts by class: {'person': 5, 'train': 2, 'total': 7}
        """
        with self._lock:
            stats = self._calculate_stats()
            stats['total'] = len(self._tracks)
            return stats
    
    def _calculate_stats(self) -> Dict[str, int]:
        """Calculate statistics by class name."""
        stats = {}
        for track in self._tracks.values():
            class_name = track.class_name
            stats[class_name] = stats.get(class_name, 0) + 1
        return stats
    
    def get_person_count(self) -> int:
        """Get count of active person tracks."""
        with self._lock:
            return self._count_by_class('person')
    
    def get_train_count(self) -> int:
        """Get count of active train tracks."""
        with self._lock:
            return self._count_by_class('train')
    
    def _count_by_class(self, class_name: str) -> int:
        """Count tracks by class name."""
        return sum(1 for track in self._tracks.values() if track.class_name == class_name)
    
    def clear(self):
        """Clear all active tracks."""
        with self._lock:
            self._tracks.clear()


# Global shared state instance
_shared_state = SharedState()


def get_shared_state() -> SharedState:
    """Get the global shared state instance."""
    return _shared_state
