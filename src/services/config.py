from dataclasses import dataclass, field
from typing import Optional

from src.core.config_loader import get_config


@dataclass
class PipelineConfig:
    source: str | int = 0
    output: Optional[str] = None
    device: Optional[str] = None
    det_model: Optional[str] = None
    imgsz: Optional[int] = None
    conf_threshold: Optional[float] = None
    nms_iou: Optional[float] = None
    conf_person: Optional[float] = None
    conf_train: Optional[float] = None
    activity_window: Optional[int] = None
    skip_clothing: Optional[bool] = None
    
    # Tracker parameters
    tracker_iou_threshold: Optional[float] = None
    tracker_max_lost: Optional[int] = None
    tracker_use_prediction: Optional[bool] = None
    
    # Activity parameters
    activity_person_speed_threshold: Optional[float] = None
    activity_vehicle_displacement_threshold: Optional[float] = None
    activity_vehicle_min_history: Optional[int] = None
    
    # Clothing detection parameters
    clothing_enabled: Optional[bool] = None
    clothing_h_min: Optional[int] = None
    clothing_h_max: Optional[int] = None
    clothing_s_min: Optional[int] = None
    clothing_v_min: Optional[int] = None
    clothing_coverage: Optional[float] = None
    
    def __post_init__(self):
        config = get_config()
        
        # Detection
        if self.det_model is None:
            self.det_model = config["detection"]["model"]
        if self.imgsz is None:
            self.imgsz = config["detection"]["image_size"]
        if self.device is None:
            self.device = config["detection"]["device"]
        
        # Confidence thresholds
        if self.conf_threshold is None:
            self.conf_threshold = config["confidence"]["threshold"]
        if self.conf_person is None:
            self.conf_person = config["confidence"]["person"]
        if self.conf_train is None:
            self.conf_train = config["confidence"]["vehicle"]
        
        # NMS
        if self.nms_iou is None:
            self.nms_iou = config["nms"]["iou_threshold"]
        
        # Tracker
        if self.tracker_iou_threshold is None:
            self.tracker_iou_threshold = config["tracker"]["iou_threshold"]
        if self.tracker_max_lost is None:
            self.tracker_max_lost = config["tracker"]["max_lost"]
        if self.tracker_use_prediction is None:
            self.tracker_use_prediction = config["tracker"]["use_prediction"]
        
        # Activity
        if self.activity_window is None:
            self.activity_window = config["activity"]["window"]
        if self.activity_person_speed_threshold is None:
            self.activity_person_speed_threshold = config["activity"]["person"]["speed_threshold"]
        if self.activity_vehicle_displacement_threshold is None:
            self.activity_vehicle_displacement_threshold = config["activity"]["vehicle"]["displacement_threshold"]
        if self.activity_vehicle_min_history is None:
            self.activity_vehicle_min_history = config["activity"]["vehicle"]["min_history"]
        
        # Clothing
        if self.skip_clothing is None:
            self.skip_clothing = not config["clothing"]["enabled"]
        if self.clothing_h_min is None:
            self.clothing_h_min = config["clothing"]["high_vis"]["h_min"]
        if self.clothing_h_max is None:
            self.clothing_h_max = config["clothing"]["high_vis"]["h_max"]
        if self.clothing_s_min is None:
            self.clothing_s_min = config["clothing"]["high_vis"]["s_min"]
        if self.clothing_v_min is None:
            self.clothing_v_min = config["clothing"]["high_vis"]["v_min"]
        if self.clothing_coverage is None:
            self.clothing_coverage = config["clothing"]["high_vis"]["coverage"]


PERSON_CLASSES = frozenset({"person"})
VEHICLE_CLASSES = frozenset({"train", "truck", "bus", "car"})
