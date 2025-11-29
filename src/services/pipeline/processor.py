from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Optional, Tuple

import cv2
import numpy as np

from src.services.config import PipelineConfig
from src.services.detector import load_model
from src.services.tracker import Tracker
from src.services.pipeline.detection import DetectionWorker
from src.services.pipeline.device import detect_device
from src.utils.visualizer import draw_tracks
from src.services.activity import ActivityClassifier

logger = logging.getLogger(__name__)


class Pipeline:
    """Main pipeline for video processing with detection and tracking."""
    
    def __init__(self, config: PipelineConfig):
        self._config = config
        self._config.device = detect_device(config.device)
        
        logger.info(f"Device: {self._config.device}")
        logger.info(f"Detection: {self._config.det_model}")
        
        self._det_model = self._load_model(config.det_model)
        self._tracker = self._create_tracker(config)
        self._classifier: Optional[ActivityClassifier] = None
    
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
        return Tracker(
            iou_threshold=config.tracker_iou_threshold or 0.2,
            max_lost=config.tracker_max_lost or 45,
            use_prediction=config.tracker_use_prediction if config.tracker_use_prediction is not None else True
        )
    
    def run(
        self,
        max_frames: Optional[int] = None,
        resize: Optional[Tuple[int, int]] = None,
        show: bool = False
    ):
        """Run pipeline on video source."""
        cap = self._open_video()
        fps, resize = self._get_video_params(cap, resize)
        
        self._classifier = self._create_classifier(fps)
        worker = DetectionWorker(self._det_model, self._tracker, self._config, self._classifier)
        worker.start()
        
        writer = self._create_writer(fps, resize)
        
        try:
            self._process(cap, worker, writer, resize, show, max_frames)
        finally:
            self._cleanup(cap, worker, writer, show)
    
    def _open_video(self) -> cv2.VideoCapture:
        """Open video source."""
        cap = cv2.VideoCapture(self._config.source)
        if not cap.isOpened():
            raise RuntimeError(f"Cannot open: {self._config.source}")
        return cap
    
    def _get_video_params(self, cap: cv2.VideoCapture, resize: Optional[Tuple[int, int]]) -> Tuple[float, Tuple[int, int]]:
        """Get video FPS and resize parameters."""
        from src.core.config_loader import get_config
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
            window=self._config.activity_window or 30,
            person_speed_threshold=self._config.activity_person_speed_threshold or 0.5,
            vehicle_displacement_threshold=self._config.activity_vehicle_displacement_threshold or 10.0,
            vehicle_min_history=self._config.activity_vehicle_min_history or 5
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
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            frame = self._resize_frame(frame, resize)
            
            worker.submit(frame)
            draw_tracks(frame, worker.get_tracks())
            
            if writer:
                writer.write(frame)
            
            if show:
                if self._handle_show_window(frame):
                    break
            
            if max_frames and frame_count >= max_frames:
                break
        
        elapsed = time.time() - start
        logger.info(f"Processed {frame_count} frames in {elapsed:.2f}s ({frame_count/elapsed:.2f} fps)")
    
    def _resize_frame(self, frame: np.ndarray, resize: Optional[Tuple[int, int]]) -> np.ndarray:
        """Resize frame if needed."""
        if resize:
            return cv2.resize(frame, resize)
        return frame
    
    def _handle_show_window(self, frame: np.ndarray) -> bool:
        """Handle window display and user input."""
        cv2.imshow("AI-Hackathon", frame)
        key = cv2.waitKey(1) & 0xFF
        return key in (ord("q"), 27)
    
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

