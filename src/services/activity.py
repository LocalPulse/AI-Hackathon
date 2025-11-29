from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List

from src.services.track import Track


@dataclass(frozen=True)
class Activity:
    """Activity classification result."""
    label: str  # "standing", "moving", or "stopped"
    confidence: float


class PersonClassifier:
    """Classifies person activity based on movement speed."""
    
    def __init__(self, speed_threshold: float = 15.0):
        self.speed_threshold = speed_threshold
    
    def classify(self, speed: float) -> Activity:
        if speed < self.speed_threshold:
            return Activity("standing", 0.90)
        return Activity("moving", 0.90)


class VehicleClassifier:
    """Classifies vehicle activity based on displacement over time."""
    
    def __init__(self, displacement_threshold: float = 8.0, min_history: int = 5):
        self.displacement_threshold = displacement_threshold
        self.min_history = min_history
    
    def classify(self, track: Track) -> Activity:
        history = getattr(track, "history", [])
        
        if len(history) < self.min_history:
            return Activity("stopped", 0.85)
        
        # Compute total displacement from start to end
        start, end = history[0], history[-1]
        displacement = math.hypot(end[0] - start[0], end[1] - start[1])
        
        if displacement < self.displacement_threshold:
            return Activity("stopped", 0.95)
        return Activity("moving", 0.90)


class ActivityClassifier:
    """Main activity classifier that routes objects to appropriate classifier."""
    
    PERSON_CLASSES = frozenset({"person"})
    VEHICLE_CLASSES = frozenset({"train", "truck", "bus", "car"})
    
    def __init__(
        self,
        fps: float = 25.0,
        window: int = 15,
        person_speed_threshold: float = 15.0,
        vehicle_displacement_threshold: float = 8.0,
        vehicle_min_history: int = 5
    ):
        self.fps = fps
        self.window = window
        self.person = PersonClassifier(person_speed_threshold)
        self.vehicle = VehicleClassifier(vehicle_displacement_threshold, vehicle_min_history)

    def update_tracks(self, tracks: List[Track]) -> None:
        for track in tracks:
            self._classify(track)

    def _classify(self, track: Track) -> None:
        cls_name = getattr(track, "cls_name", None)
        
        if cls_name in self.PERSON_CLASSES:
            speed = self._compute_speed(track)
            result = self.person.classify(speed)
        elif cls_name in self.VEHICLE_CLASSES:
            result = self.vehicle.classify(track)
        else:
            track.activity = None
            track.activity_conf = 0.0
            return
        
        track.activity = result.label
        track.activity_conf = result.confidence

    def _compute_speed(self, track: Track) -> float:
        """Compute speed in pixels per second using median of recent distances."""
        history = getattr(track, "history", [])
        
        if len(history) < 3:
            return 0.0
        
        pts = history[-self.window:]
        distances = [
            math.hypot(pts[i][0] - pts[i-1][0], pts[i][1] - pts[i-1][1])
            for i in range(1, len(pts))
        ]
        
        if not distances:
            return 0.0
        
        # Use median to reduce noise
        distances.sort()
        median_distance = distances[len(distances) // 2]
        return median_distance * self.fps


__all__ = ["ActivityClassifier", "Activity"]
