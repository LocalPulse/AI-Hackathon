import logging
from typing import List, Tuple, Optional

import numpy as np

from src.services.config import PipelineConfig, PERSON_CLASSES, VEHICLE_CLASSES
from src.services.pipeline.utils import get_class_name

logger = logging.getLogger(__name__)


class FrameDetector:
    
    def __init__(self, det_model, config: PipelineConfig):
        self._det_model = det_model
        self._config = config
    
    def detect(self, frame: np.ndarray) -> List[Tuple]:
        """Run object detection on frame."""
        if self._det_model is None:
            return []
        
        try:
            results = self._det_model.predict(
                source=frame,
                imgsz=self._config.imgsz,
                conf=self._config.conf_threshold,
                iou=self._config.nms_iou,
                save=False,
                verbose=False,
                device=self._config.device
            )
        except Exception as e:
            logger.warning(f"Detection failed: {e}")
            return []
        
        return self._extract_detections(results)
    
    def _extract_detections(self, results) -> List[Tuple]:
        """Extract detections from YOLO results."""
        detections = []
        for r in results:
            detections.extend(self._parse_result(r))
        return detections
    
    def _parse_result(self, result) -> List[Tuple]:
        """Parse single YOLO result."""
        try:
            boxes = result.boxes.xyxy.cpu().numpy()
            confs = result.boxes.conf.cpu().numpy()
            classes = result.boxes.cls.cpu().numpy().astype(int)
            
            return [
                (*map(float, box[:4]), int(cls_id), float(score))
                for box, cls_id, score in zip(boxes, classes, confs)
            ]
        except Exception:
            return []
    
    def filter(self, detections: List[Tuple]) -> List[Tuple]:
        """Filter detections by class-specific confidence thresholds."""
        names = getattr(self._det_model, 'names', None)
        result = []
        
        for det in detections:
            cls_name = get_class_name(names, det[4])
            threshold = self._get_threshold(cls_name)
            
            if threshold is None:
                continue
            
            if det[5] >= threshold:
                result.append(det)
        
        return result
    
    def _get_threshold(self, cls_name: Optional[str]) -> Optional[float]:
        """Get confidence threshold for class."""
        if cls_name in PERSON_CLASSES:
            return self._config.conf_person
        if cls_name in VEHICLE_CLASSES:
            return self._config.conf_train
        return None

