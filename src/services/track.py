from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple, Optional
import time
import numpy as np


@dataclass
class Track:
    """Represents a tracked object across multiple frames."""
    id: int
    bbox: Tuple[float, float, float, float]  # (x1, y1, x2, y2)
    cls: int
    score: float
    last_seen: float = field(default_factory=time.time)
    hits: int = 1
    lost_frames: int = 0
    history: List[Tuple[int, int]] = field(default_factory=list)  # Center positions
    velocity: Tuple[float, float] = (0.0, 0.0)  # (vx, vy) pixels per frame
    clothing: Optional[str] = None
    motion_buffer: List[float] = field(default_factory=list)
    activity: Optional[str] = None  # "standing", "moving", "stopped"
    activity_conf: float = 0.0
    activity_history: List = field(default_factory=list)
    keypoints: Optional[np.ndarray] = None
    cls_name: Optional[str] = None
    previous_activity: Optional[str] = None


    def predict_bbox(self) -> Tuple[float, float, float, float]:
        """Predict next bbox position using velocity."""
        x1, y1, x2, y2 = self.bbox
        vx, vy = self.velocity
        return (x1 + vx, y1 + vy, x2 + vx, y2 + vy)

    def update_velocity(self):
        """Update velocity from position history using weighted average."""
        if len(self.history) < 2:
            self.velocity = (0.0, 0.0)
            return
        
        n = min(5, len(self.history))
        pts = self.history[-n:]
        
        # Weighted average: more recent = higher weight
        total_vx, total_vy, total_w = 0.0, 0.0, 0.0
        for i in range(1, len(pts)):
            weight = i
            vx = pts[i][0] - pts[i-1][0]
            vy = pts[i][1] - pts[i-1][1]
            total_vx += vx * weight
            total_vy += vy * weight
            total_w += weight
        
        self.velocity = (total_vx / total_w, total_vy / total_w) if total_w > 0 else (0.0, 0.0)

    def add_position(self, cx: int, cy: int, max_history: int = 50):
        self.history.append((cx, cy))
        if len(self.history) > max_history:
            self.history.pop(0)

    @property
    def center(self) -> Tuple[int, int]:
        x1, y1, x2, y2 = self.bbox
        return int((x1 + x2) / 2), int((y1 + y2) / 2)

