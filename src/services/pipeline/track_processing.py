import logging
import time
from typing import List, Optional

from src.services.tracker import Track
from src.services.activity import ActivityClassifier
from src.services.pipeline.utils import get_class_name
from src.utils.data_base import log_activity
from src.utils.constants import PERIODIC_LOG_INTERVAL, DEFAULT_CAMERA_ID
from src.utils.state_sync import save_camera_tracks

logger = logging.getLogger(__name__)

VALID_CLASSES = frozenset(['person', 'train'])


class TrackProcessor:
    """Processes tracks: classifies activity, logs to database, updates shared state."""
    def __init__(self, det_model, classifier: Optional[ActivityClassifier], camera_id: Optional[str] = None):
        self._det_model = det_model
        self._classifier = classifier
        self._camera_id = camera_id or DEFAULT_CAMERA_ID
        self._last_periodic_log_time = 0.0
    
    def process(self, tracks: List[Track]):
        """Process tracks: classify, log and update shared state."""
        self._classify(tracks)
        self._log_activity_changes(tracks)
        self._update_shared_state(tracks)
    
    def _classify(self, tracks: List[Track]):
        """Classify activity for tracks."""
        names = getattr(self._det_model, 'names', None)
        for track in tracks:
            track.cls_name = get_class_name(names, track.cls)
        
        if not self._classifier:
            return
        self._classifier.update_tracks(tracks)
    
    def _log_activity_changes(self, tracks: List[Track]):
        """Log activities to database when activity changes or periodically."""
        if log_activity is None:
            return
        
        current_time = time.time()
        should_periodic_log = self._should_periodic_log(current_time)
        
        for track in tracks:
            if self._should_log_track_change(track):
                self._log_track_activity(track)
                continue
            
            if should_periodic_log and self._should_periodic_log_track(track):
                self._log_track_activity(track, force=True)
        
        if should_periodic_log:
            self._last_periodic_log_time = current_time
    
    def _should_periodic_log(self, current_time: float) -> bool:
        """Check if periodic logging should occur."""
        return (current_time - self._last_periodic_log_time) >= PERIODIC_LOG_INTERVAL
    
    def _is_valid_track_class(self, track: Track) -> bool:
        """Check if track class is valid for logging."""
        return track.cls_name in VALID_CLASSES
    
    def _has_activity(self, track: Track) -> bool:
        """Check if track has activity."""
        return bool(track.activity)
    
    def _should_log_track_change(self, track: Track) -> bool:
        """Check if track should be logged due to activity change."""
        if not self._is_valid_track_class(track):
            return False
        
        if not self._has_activity(track):
            return False
        
        if track.previous_activity is None:
            return True
        
        return track.activity != track.previous_activity
    
    def _should_periodic_log_track(self, track: Track) -> bool:
        """Check if track should be logged periodically."""
        if not self._is_valid_track_class(track):
            return False
        return self._has_activity(track)
    
    def _log_track_activity(self, track: Track, force: bool = False):
        """Log track activity to database."""
        if log_activity is None:
            return
        
        if not track.cls_name or not track.activity:
            return
        
        try:
            log_activity(
                track_id=track.id,
                class_name=track.cls_name,
                activity=track.activity,
                confidence=track.activity_conf,
                camera_id=self._camera_id
            )
            if not force:
                track.previous_activity = track.activity
        except Exception as e:
            logger.warning(f"Failed to log activity: {e}")
    
    def _update_shared_state(self, tracks: List[Track]):
        """Update sync file with current active tracks."""
        track_data = self._prepare_track_data(tracks)
        
        try:
            save_camera_tracks(self._camera_id, track_data, time.time())
        except Exception as e:
            logger.warning(f"Failed to save camera tracks: {e}")
    
    def _prepare_track_data(self, tracks: List[Track]) -> List[dict]:
        """Prepare track data for shared state."""
        return [
            {
                'track_id': track.id,
                'class_name': track.cls_name or 'unknown',
                'activity': track.activity or 'unknown',
                'confidence': track.activity_conf
            }
            for track in tracks
            if self._is_valid_track_class(track)
        ]

