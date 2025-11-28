from __future__ import annotations

import logging
import queue
import threading
import time
from pathlib import Path
from typing import List, Optional, Tuple, Any, Dict

import cv2
import numpy as np

from src.services.config import PipelineConfig, PERSON_CLASSES, VEHICLE_CLASSES
from src.services.detector import load_model
from src.services.tracker import Tracker, Track
from src.utils.visualizer import draw_tracks

try:
    from src.services.activity import ActivityClassifier
except ImportError:
    ActivityClassifier = None

logger = logging.getLogger(__name__)


def detect_device(requested: Optional[str] = None) -> str:
    if requested:
        return requested
    try:
        import torch
        if torch.cuda.is_available():
            logger.info(f"CUDA: {torch.cuda.get_device_name(0)}")
            return "cuda"
    except Exception:
        pass
    return "cpu"


def get_class_name(names: Optional[Dict], cls_id: int) -> Optional[str]:
    if names is None:
        return None
    try:
        return names.get(cls_id) if isinstance(names, dict) else names[cls_id]
    except (IndexError, KeyError):
        return None


class Worker:
    def __init__(self, det_model, tracker: Tracker, config: PipelineConfig, classifier):
        self._det_model = det_model
        self._tracker = tracker
        self._config = config
        self._classifier = classifier
        self._queue: queue.Queue = queue.Queue(maxsize=1)  # Single frame buffer
        self._tracks: List[Track] = []
        self._lock = threading.Lock()
        self._running = False
        self._thread = None

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)

    def submit(self, frame: np.ndarray):
        """Submit frame for processing (drops old frame if queue is full)."""
        try:
            self._queue.put_nowait(frame.copy())
        except queue.Full:
            try:
                self._queue.get_nowait()  # Drop oldest frame
                self._queue.put_nowait(frame.copy())
            except Exception:
                pass

    def get_tracks(self) -> List[Track]:
        with self._lock:
            return list(self._tracks)

    def _loop(self):
        """Main processing loop: detect -> filter -> track -> classify."""
        while self._running:
            try:
                frame = self._queue.get(timeout=0.01)
            except queue.Empty:
                continue
            
            detections = self._detect(frame)
            detections = self._filter(detections)  # Apply class-specific thresholds
            
            self._tracker.update(detections)
            tracks = list(self._tracker.tracks.values())
            
            self._classify(tracks)  # Activity classification
            self._detect_clothing(frame, tracks)  # PPE detection
            
            with self._lock:
                self._tracks = tracks

    def _detect(self, frame: np.ndarray) -> List[Tuple]:
        if self._det_model is None:
            return []
        try:
            results = self._det_model.predict(
                source=frame, imgsz=self._config.imgsz,
                conf=self._config.conf_threshold, iou=self._config.nms_iou,
                save=False, verbose=False, device=self._config.device
            )
        except Exception as e:
            logger.warning(f"Detection failed: {e}")
            return []
        
        detections = []
        for r in results:
            try:
                boxes = r.boxes.xyxy.cpu().numpy()
                confs = r.boxes.conf.cpu().numpy()
                classes = r.boxes.cls.cpu().numpy().astype(int)
                for box, cls_id, score in zip(boxes, classes, confs):
                    detections.append((*map(float, box[:4]), int(cls_id), float(score)))
            except Exception:
                continue
        return detections

    def _filter(self, detections: List[Tuple]) -> List[Tuple]:
        names = getattr(self._det_model, 'names', None)
        result = []
        for det in detections:
            cls_name = get_class_name(names, det[4])
            if cls_name in PERSON_CLASSES:
                thr = self._config.conf_person
            elif cls_name in VEHICLE_CLASSES:
                thr = self._config.conf_train
            else:
                continue  # Skip unknown classes
            if det[5] >= thr:
                result.append(det)
        return result

    def _classify(self, tracks: List[Track]):
        names = getattr(self._det_model, 'names', None)
        for track in tracks:
            track.cls_name = get_class_name(names, track.cls)
        if self._classifier:
            self._classifier.update_tracks(tracks)

    def _detect_clothing(self, frame: np.ndarray, tracks: List[Track]):
        """Detect high-visibility clothing for person tracks."""
        if self._config.skip_clothing:
            return
        for track in tracks:
            if track.cls_name != "person":
                track.clothing = None
                continue
            x1, y1, x2, y2 = map(int, track.bbox)
            if x2 <= x1 or y2 <= y1:
                track.clothing = "unknown"
                continue
            # Check upper 45% of bounding box (torso area)
            torso = frame[y1:y1 + int((y2 - y1) * 0.45), x1:x2]
            track.clothing = "high-vis" if self._has_high_vis(torso) else "none"

    def _has_high_vis(self, img: np.ndarray) -> bool:
        if img is None or img.size == 0:
            return False
        try:
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            h, s, v = cv2.split(hsv)
            mask = (
                (h >= self._config.clothing_h_min) & (h <= self._config.clothing_h_max)
            ) & (s >= self._config.clothing_s_min) & (v >= self._config.clothing_v_min)
            return mask.sum() / (mask.size + 1e-6) > self._config.clothing_coverage
        except Exception:
            return False


class Pipeline:
    def __init__(self, config: PipelineConfig):
        self._config = config
        self._config.device = detect_device(config.device)
        
        logger.info(f"Device: {self._config.device}")
        logger.info(f"Detection: {self._config.det_model}")
        
        self._det_model = self._load_model(config.det_model)
        self._tracker = Tracker(
            iou_threshold=config.tracker_iou_threshold,
            max_lost=config.tracker_max_lost,
            use_prediction=config.tracker_use_prediction
        )
        self._classifier = None  # Initialized in run() with FPS

    def _load_model(self, name: str):
        if not name:
            return None
        try:
            return load_model(name, device=self._config.device)
        except Exception as e:
            logger.error(f"Failed to load {name}: {e}")
            return None

    def run(self, max_frames: Optional[int] = None, resize: Optional[Tuple[int, int]] = None, show: bool = False):
        cap = cv2.VideoCapture(self._config.source)
        if not cap.isOpened():
            raise RuntimeError(f"Cannot open: {self._config.source}")
        
        from src.core.config_loader import get_config
        config = get_config()
        default_fps = config["video"]["default_fps"]
        default_resize = tuple(config["video"]["resize"])
        
        if resize is None:
            resize = default_resize
        
        fps = float(cap.get(cv2.CAP_PROP_FPS)) or default_fps
        
        if ActivityClassifier:
            self._classifier = ActivityClassifier(
                fps=fps,
                window=self._config.activity_window,
                person_speed_threshold=self._config.activity_person_speed_threshold,
                vehicle_displacement_threshold=self._config.activity_vehicle_displacement_threshold,
                vehicle_min_history=self._config.activity_vehicle_min_history
            )
        
        worker = Worker(self._det_model, self._tracker, self._config, self._classifier)
        worker.start()
        
        writer = self._create_writer(fps, resize) if self._config.output else None
        
        try:
            self._process(cap, worker, writer, resize, show, max_frames)
        finally:
            worker.stop()
            cap.release()
            if writer:
                writer.release()
            if show:
                cv2.destroyAllWindows()

    def _create_writer(self, fps: float, size: Tuple[int, int]) -> cv2.VideoWriter:
        Path(self._config.output).parent.mkdir(parents=True, exist_ok=True)
        return cv2.VideoWriter(self._config.output, cv2.VideoWriter_fourcc(*"mp4v"), fps, size)

    def _process(self, cap, worker, writer, resize, show, max_frames):
        """Main processing loop: read frames, process, visualize, and save."""
        frame_count = 0
        start = time.time()
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            if resize:
                frame = cv2.resize(frame, resize)
            
            worker.submit(frame)  # Async processing
            draw_tracks(frame, worker.get_tracks())  # Draw current tracks
            
            if writer:
                writer.write(frame)
            
            if show:
                cv2.imshow("AI-Hackathon", frame)
                if cv2.waitKey(1) & 0xFF in (ord("q"), 27):  # 'q' or ESC to quit
                    break
            
            if max_frames and frame_count >= max_frames:
                break
        
        elapsed = time.time() - start
        logger.info(f"Processed {frame_count} frames in {elapsed:.2f}s ({frame_count/elapsed:.2f} fps)")
