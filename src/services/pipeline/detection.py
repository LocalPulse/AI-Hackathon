import logging
import queue
import threading
from typing import List, Optional

import numpy as np

from src.services.config import PipelineConfig
from src.services.tracker import Tracker, Track
from src.services.pipeline.frame_detection import FrameDetector
from src.services.pipeline.track_processing import TrackProcessor
from src.services.activity import ActivityClassifier

logger = logging.getLogger(__name__)


class DetectionWorker:
    """Worker thread for async frame processing."""
    
    def __init__(
        self,
        det_model,
        tracker: Tracker,
        config: PipelineConfig,
        classifier: Optional[ActivityClassifier]
    ):
        self._tracker = tracker
        self._frame_detector = FrameDetector(det_model, config)
        self._track_processor = TrackProcessor(det_model, classifier)
        
        self._queue: queue.Queue = queue.Queue(maxsize=1)
        self._tracks: List[Track] = []
        self._lock = threading.Lock()
        self._running = False
        self._thread: Optional[threading.Thread] = None
    
    def start(self):
        """Start worker thread."""
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
    
    def stop(self):
        """Stop worker thread."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
    
    def submit(self, frame: np.ndarray):
        """Submit frame for processing."""
        try:
            self._queue.put_nowait(frame.copy())
        except queue.Full:
            self._drop_old_frame(frame)
    
    def _drop_old_frame(self, frame: np.ndarray):
        """Drop oldest frame and add new one."""
        try:
            self._queue.get_nowait()
            self._queue.put_nowait(frame.copy())
        except Exception:
            pass
    
    def get_tracks(self) -> List[Track]:
        """Get current tracks (thread-safe)."""
        with self._lock:
            return list(self._tracks)
    
    def _loop(self):
        """Main processing loop."""
        while self._running:
            frame = self._get_frame()
            if frame is None:
                continue
            
            tracks = self._process_frame(frame)
            self._update_tracks(tracks)
    
    def _get_frame(self) -> Optional[np.ndarray]:
        """Get frame from queue."""
        try:
            return self._queue.get(timeout=0.01)
        except queue.Empty:
            return None
    
    def _process_frame(self, frame: np.ndarray) -> List[Track]:
        """Process single frame through detection pipeline."""
        detections = self._frame_detector.detect(frame)
        detections = self._frame_detector.filter(detections)
        
        self._tracker.update(detections)
        tracks = list(self._tracker.tracks.values())
        
        self._track_processor.process(tracks)
        
        return tracks
    
    def _update_tracks(self, tracks: List[Track]):
        """Update tracks (thread-safe)."""
        with self._lock:
            self._tracks = tracks
