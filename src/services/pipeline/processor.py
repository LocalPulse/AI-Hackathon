from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import List, Optional, Tuple

import cv2
import numpy as np

from src.services.config import PipelineConfig
from src.services.detector import load_model
from src.services.tracker import Tracker
from src.services.pipeline.detection import DetectionWorker
from src.services.pipeline.device import detect_device
from src.utils.visualizer import draw_tracks
from src.services.activity import ActivityClassifier
from src.utils.constants import (
    LOG_INTERVAL,
    HEARTBEAT_INTERVAL,
    DEFAULT_IOU_THRESHOLD,
    DEFAULT_MAX_LOST,
    DEFAULT_ACTIVITY_WINDOW,
    DEFAULT_PERSON_SPEED_THRESHOLD,
    DEFAULT_VEHICLE_DISPLACEMENT_THRESHOLD,
    DEFAULT_VEHICLE_MIN_HISTORY,
    WINDOW_NAME,
    QUIT_KEYS,
)
from src.utils.state_sync import (
    register_camera_start,
    register_camera_stop,
    heartbeat_camera,
)
from src.core.config import get_config

logger = logging.getLogger(__name__)


class Pipeline:
    
    def __init__(self, config: PipelineConfig, camera_id: Optional[str] = None):
        self._config = config
        self._config.device = detect_device(config.device)
        self._camera_id = camera_id
        
        self._log_init_info()
        
        self._det_model = self._load_model(config.det_model)
        self._tracker = self._create_tracker(config)
        self._classifier: Optional[ActivityClassifier] = None
    
    def _log_init_info(self):
        """Log initialization information."""
        logger.info(f"Device: {self._config.device}")
        logger.info(f"Detection: {self._config.det_model}")
        if self._camera_id:
            logger.info(f"Camera ID: {self._camera_id}")
    
    def _load_model(self, model_name: Optional[str]):
        """Load detection model."""
        if not model_name:
            return None
        
        try:
            return load_model(model_name, device=self._config.device)
        except Exception as e:
            logger.error(f"Failed to load {model_name}: {e}")
            return None
    
    def _create_tracker(self, config: PipelineConfig) -> Tracker:
        """Create tracker with configuration."""
        iou_threshold = config.tracker_iou_threshold or DEFAULT_IOU_THRESHOLD
        max_lost = config.tracker_max_lost or DEFAULT_MAX_LOST
        use_prediction = config.tracker_use_prediction if config.tracker_use_prediction is not None else True
        
        return Tracker(
            iou_threshold=iou_threshold,
            max_lost=max_lost,
            use_prediction=use_prediction
        )
    
    def run(
        self,
        max_frames: Optional[int] = None,
        resize: Optional[Tuple[int, int]] = None,
        show: bool = False
    ):
        """Run pipeline on video source."""
        self._register_camera_start()
        
        cap = self._open_video()
        fps, resize = self._get_video_params(cap, resize)
        
        self._classifier = self._create_classifier(fps)
        worker = self._create_worker()
        worker.start()
        
        writer = self._create_writer(fps, resize)
        
        try:
            self._process(cap, worker, writer, resize, show, max_frames)
        finally:
            self._register_camera_stop()
            self._cleanup(cap, worker, writer, show)
    
    def _create_worker(self) -> DetectionWorker:
        """Create detection worker."""
        return DetectionWorker(
            self._det_model,
            self._tracker,
            self._config,
            self._classifier,
            camera_id=self._camera_id
        )
    
    def _register_camera_start(self):
        """Register camera start event."""
        if not self._camera_id:
            return
        
        try:
            register_camera_start(self._camera_id)
        except Exception as e:
            logger.warning(f"Failed to register camera start: {e}")
    
    def _register_camera_stop(self):
        """Register camera stop event."""
        if not self._camera_id:
            return
        
        try:
            register_camera_stop(self._camera_id)
        except Exception as e:
            logger.warning(f"Failed to register camera stop: {e}")
    
    def _open_video(self) -> cv2.VideoCapture:
        """Open video source."""
        cap = cv2.VideoCapture(self._config.source)
        if not cap.isOpened():
            raise RuntimeError(f"Cannot open: {self._config.source}")
        return cap
    
    def _get_video_params(self, cap: cv2.VideoCapture, resize: Optional[Tuple[int, int]]) -> Tuple[float, Tuple[int, int]]:
        """Get video FPS and resize parameters."""
        config = get_config()
        
        default_fps = config["video"]["default_fps"]
        default_resize = tuple(config["video"]["resize"])
        
        fps = float(cap.get(cv2.CAP_PROP_FPS)) or default_fps
        resize = resize or default_resize
        
        return fps, resize
    
    def _create_classifier(self, fps: float) -> ActivityClassifier:
        """Create activity classifier."""
        return ActivityClassifier(
            fps=fps,
            window=self._config.activity_window or DEFAULT_ACTIVITY_WINDOW,
            person_speed_threshold=self._config.activity_person_speed_threshold or DEFAULT_PERSON_SPEED_THRESHOLD,
            vehicle_displacement_threshold=self._config.activity_vehicle_displacement_threshold or DEFAULT_VEHICLE_DISPLACEMENT_THRESHOLD,
            vehicle_min_history=self._config.activity_vehicle_min_history or DEFAULT_VEHICLE_MIN_HISTORY
        )
    
    def _create_writer(self, fps: float, size: Tuple[int, int]) -> Optional[cv2.VideoWriter]:
        """Create video writer if output path is specified."""
        if not self._config.output:
            return None
        
        Path(self._config.output).parent.mkdir(parents=True, exist_ok=True)
        return cv2.VideoWriter(
            self._config.output,
            cv2.VideoWriter.fourcc(*"mp4v"),
            fps,
            size
        )
    
    def _process(
        self,
        cap: cv2.VideoCapture,
        worker: DetectionWorker,
        writer: Optional[cv2.VideoWriter],
        resize: Tuple[int, int],
        show: bool,
        max_frames: Optional[int]
    ):
        """Main processing loop."""
        frame_count = 0
        start = time.time()
        last_log_time = start
        last_heartbeat_time = start
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            frame = self._resize_frame(frame, resize)
            
            tracks = self._process_frame(worker, frame)
            self._write_frame(writer, frame)
            
            if self._should_quit(show, frame):
                break
            
            current_time = time.time()
            last_heartbeat_time = self._update_heartbeat(current_time, last_heartbeat_time)
            last_log_time = self._update_logging(frame_count, tracks, current_time, start, last_log_time)
            
            if self._should_stop(frame_count, max_frames):
                break
        
        self._log_final_stats(frame_count, start)
    
    def _process_frame(self, worker: DetectionWorker, frame: np.ndarray) -> List:
        """Process frame through detection worker."""
        worker.submit(frame)
        tracks = worker.get_tracks()
        draw_tracks(frame, tracks)
        return tracks
    
    def _write_frame(self, writer: Optional[cv2.VideoWriter], frame: np.ndarray):
        """Write frame to video writer if available."""
        if writer:
            writer.write(frame)
    
    def _should_quit(self, show: bool, frame: np.ndarray) -> bool:
        """Check if processing should quit."""
        if not show:
            return False
        return self._handle_show_window(frame)
    
    def _update_heartbeat(self, current_time: float, last_heartbeat_time: float) -> float:
        """Update heartbeat if needed."""
        if current_time - last_heartbeat_time < HEARTBEAT_INTERVAL:
            return last_heartbeat_time
        
        self._send_heartbeat_if_needed()
        return current_time
    
    def _update_logging(self, frame_count: int, tracks: List, current_time: float, start: float, last_log_time: float) -> float:
        """Update logging if needed."""
        if current_time - last_log_time < LOG_INTERVAL:
            return last_log_time
        
        self._log_progress(frame_count, tracks, current_time, start)
        return current_time
    
    def _should_stop(self, frame_count: int, max_frames: Optional[int]) -> bool:
        """Check if processing should stop."""
        if not max_frames:
            return False
        return frame_count >= max_frames
    
    def _log_final_stats(self, frame_count: int, start: float):
        """Log final processing statistics."""
        elapsed = time.time() - start
        camera_info = self._format_camera_info()
        fps = frame_count / elapsed if elapsed > 0 else 0
        
        logger.info(
            f"Camera{camera_info}: "
            f"Processed {frame_count} frames in {elapsed:.2f}s ({fps:.2f} fps)"
        )
    
    def _format_camera_info(self) -> str:
        """Format camera ID for logging."""
        if not self._camera_id:
            return ""
        return f" [{self._camera_id}]"
    
    def _resize_frame(self, frame: np.ndarray, resize: Optional[Tuple[int, int]]) -> np.ndarray:
        """Resize frame if needed."""
        if resize:
            return cv2.resize(frame, resize)
        return frame
    
    def _send_heartbeat_if_needed(self):
        """Send heartbeat to keep camera active."""
        if not self._camera_id:
            return
        
        try:
            heartbeat_camera(self._camera_id)
        except Exception as e:
            logger.warning(f"Failed to send heartbeat: {e}")
    
    def _log_progress(self, frame_count: int, tracks: List, current_time: float, start: float):
        """Log processing progress."""
        person_count = self._count_tracks_by_class(tracks, 'person')
        train_count = self._count_tracks_by_class(tracks, 'train')
        fps = self._calculate_fps(frame_count, current_time, start)
        camera_info = self._format_camera_info()
        
        logger.info(
            f"Camera{camera_info}: Frame {frame_count} | "
            f"People: {person_count} | Trains: {train_count} | "
            f"FPS: {fps:.1f}"
        )
    
    def _count_tracks_by_class(self, tracks: List, class_name: str) -> int:
        """Count tracks by class name."""
        return sum(1 for t in tracks if t.cls_name == class_name)
    
    def _calculate_fps(self, frame_count: int, current_time: float, start: float) -> float:
        """Calculate current FPS."""
        elapsed = current_time - start
        return frame_count / elapsed if elapsed > 0 else 0.0
    
    def _handle_show_window(self, frame: np.ndarray) -> bool:
        """Handle window display and user input."""
        cv2.imshow(WINDOW_NAME, frame)
        key = cv2.waitKey(1) & 0xFF
        return key in QUIT_KEYS
    
    def _cleanup(
        self,
        cap: cv2.VideoCapture,
        worker: DetectionWorker,
        writer: Optional[cv2.VideoWriter],
        show: bool
    ):
        """Cleanup resources."""
        worker.stop()
        cap.release()
        
        if writer:
            writer.release()
        
        if show:
            cv2.destroyAllWindows()

