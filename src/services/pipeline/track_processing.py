import logging
from typing import List, Optional

from src.services.tracker import Track
from src.services.activity import ActivityClassifier
from src.services.pipeline.utils import get_class_name
from src.utils.data_base import log_activity
from src.utils.shared_state import get_shared_state

logger = logging.getLogger(__name__)


class TrackProcessor:
    def __init__(self, det_model, classifier: Optional[ActivityClassifier]):
        self._det_model = det_model
        self._classifier = classifier
    
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
        
        if self._classifier:
            self._classifier.update_tracks(tracks)
    
    def _log_activity_changes(self, tracks: List[Track]):
        """Log activities to database when activity changes."""
        if log_activity is None:
            return
        
        for track in tracks:
            if not self._should_log_track(track):
                continue
            
            self._log_track_activity(track)
    
    def _should_log_track(self, track: Track) -> bool:
        """Check if track should be logged."""
        if track.cls_name not in ['person', 'train']:
            return False
        
        if not track.activity:
            return False
        
        if track.activity == track.previous_activity:
            return False
        
        return True
    
    def _log_track_activity(self, track: Track):
        """Log track activity to database."""
        if log_activity is None:
            return
        
        if track.cls_name is None or track.activity is None:
            return
        
        try:
            log_activity(
                track_id=track.id,
                class_name=track.cls_name,
                activity=track.activity,
                confidence=track.activity_conf
            )
            track.previous_activity = track.activity
        except Exception as e:
            logger.warning(f"Failed to log activity: {e}")
    
    def _update_shared_state(self, tracks: List[Track]):
        """Update shared state with current active tracks."""
        if get_shared_state is None:
            return
        
        try:
            shared_state = get_shared_state()
            track_data = self._prepare_track_data(tracks)
            shared_state.update_tracks(track_data)
        except Exception as e:
            logger.warning(f"Failed to update shared state: {e}")
    
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
            if track.cls_name in ['person', 'train']
        ]

