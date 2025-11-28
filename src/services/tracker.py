from __future__ import annotations

from typing import Dict, List, Tuple, Set
import time
import numpy as np

from src.services.track import Track

# Type aliases
BBox = Tuple[float, float, float, float]
Detection = Tuple[float, float, float, float, int, float]  # x1, y1, x2, y2, cls, score


def compute_iou(box_a: BBox, box_b: BBox) -> float:
    """Compute Intersection over Union between two bounding boxes."""
    xa1, ya1, xa2, ya2 = box_a
    xb1, yb1, xb2, yb2 = box_b
    
    xi1, yi1 = max(xa1, xb1), max(ya1, yb1)
    xi2, yi2 = min(xa2, xb2), min(ya2, yb2)
    
    inter = max(0, xi2 - xi1) * max(0, yi2 - yi1)
    area_a = max(0, xa2 - xa1) * max(0, ya2 - ya1)
    area_b = max(0, xb2 - xb1) * max(0, yb2 - yb1)
    union = area_a + area_b - inter
    
    return inter / union if union > 0 else 0.0


class Matcher:
    def __init__(self, iou_threshold: float):
        self.iou_threshold = iou_threshold
    
    def match(self, detections: List[BBox], tracks: Dict[int, Track], use_prediction: bool) -> Dict[int, int]:
        """Match detections to tracks using greedy IoU matching.
        
        Returns:
            Mapping from detection index to track_id
        """
        if not tracks or not detections:
            return {}
        
        track_ids = list(tracks.keys())
        track_boxes = [self._get_track_box(tracks[tid], use_prediction) for tid in track_ids]
        iou_matrix = self._build_iou_matrix(detections, track_boxes)
        
        return self._greedy_match(iou_matrix, track_ids)
    
    def _get_track_box(self, track: Track, use_prediction: bool) -> BBox:
        """Get bounding box for matching (predicted or current)."""
        if track.lost_frames > 0 and use_prediction:
            return track.predict_bbox()
        return track.bbox
    
    def _build_iou_matrix(self, detections: List[BBox], track_boxes: List[BBox]) -> np.ndarray:
        """Build IoU matrix between detections and tracks."""
        matrix = np.zeros((len(detections), len(track_boxes)))
        for i, det_box in enumerate(detections):
            for j, track_box in enumerate(track_boxes):
                matrix[i, j] = compute_iou(det_box, track_box)
        return matrix
    
    def _greedy_match(self, iou_matrix: np.ndarray, track_ids: List[int]) -> Dict[int, int]:
        mapping: Dict[int, int] = {}
        used_dets: Set[int] = set()
        used_tracks: Set[int] = set()
        
        while iou_matrix.size > 0:
            i, j = np.unravel_index(iou_matrix.argmax(), iou_matrix.shape)
            iou_value = iou_matrix[i, j]
            
            if iou_value < self.iou_threshold:
                break
            
            if i not in used_dets and j not in used_tracks:
                mapping[i] = track_ids[j]
                used_dets.add(i)
                used_tracks.add(j)
            
            iou_matrix[i, j] = 0
        
        return mapping


class TrackManager:
    def __init__(self, max_lost: int, use_prediction: bool):
        self.max_lost = max_lost
        self.use_prediction = use_prediction
        self._next_id = 1
    
    def create_track(self, box: BBox, cls: int, score: float) -> Track:
        cx, cy = int((box[0] + box[2]) / 2), int((box[1] + box[3]) / 2)
        track = Track(
            id=self._next_id,
            bbox=box,
            cls=cls,
            score=score,
            history=[(cx, cy)]
        )
        self._next_id += 1
        return track
    
    def update_track(self, track: Track, box: BBox, cls: int, score: float):
        track.bbox = box
        track.cls = cls
        track.score = score
        track.last_seen = time.time()
        track.hits += 1
        track.lost_frames = 0
        track.add_position(*track.center)
        track.update_velocity()
    
    def update_lost_tracks(self, tracks: Dict[int, Track], updated_ids: Set[int]):
        for track_id, track in list(tracks.items()):
            if track_id in updated_ids:
                continue
            
            track.lost_frames += 1
            
            if self._should_predict(track):
                self._apply_prediction(track)
            
            if track.lost_frames > self.max_lost:
                del tracks[track_id]
    
    def _should_predict(self, track: Track) -> bool:
        """Check if track should use prediction."""
        return self.use_prediction and track.lost_frames <= self.max_lost
    
    def _apply_prediction(self, track: Track):
        decay = max(0.5, 1.0 - track.lost_frames * 0.02)
        vx, vy = track.velocity
        track.velocity = (vx * decay, vy * decay)
        track.bbox = track.predict_bbox()
        track.add_position(*track.center)


class Tracker:
    def __init__(self, iou_threshold: float = 0.2, max_lost: int = 45, use_prediction: bool = True):
        self.matcher = Matcher(iou_threshold)
        self.track_manager = TrackManager(max_lost, use_prediction)
        self.tracks: Dict[int, Track] = {}
    
    def update(self, detections: List[Detection]):
        boxes = [tuple(d[:4]) for d in detections]
        classes = [int(d[4]) for d in detections]
        scores = [float(d[5]) for d in detections]
        
        mapping = self.matcher.match(boxes, self.tracks, self.track_manager.use_prediction)
        updated_ids = self._update_matched_tracks(mapping, boxes, classes, scores)
        self._create_new_tracks(mapping, boxes, classes, scores)
        self.track_manager.update_lost_tracks(self.tracks, updated_ids)
    
    def _update_matched_tracks(self, mapping: Dict[int, int], boxes: List[BBox], 
                               classes: List[int], scores: List[float]) -> Set[int]:
        updated_ids: Set[int] = set()
        for det_idx, track_id in mapping.items():
            self.track_manager.update_track(
                self.tracks[track_id],
                boxes[det_idx],
                classes[det_idx],
                scores[det_idx]
            )
            updated_ids.add(track_id)
        return updated_ids
    
    def _create_new_tracks(self, mapping: Dict[int, int], boxes: List[BBox],
                          classes: List[int], scores: List[float]):
        """Create tracks for unmatched detections."""
        for i, box in enumerate(boxes):
            if i not in mapping:
                track = self.track_manager.create_track(box, classes[i], scores[i])
                self.tracks[track.id] = track
    
    def reset(self):
        self.track_manager._next_id = 1
        self.tracks.clear()


# Backward compatibility
IouTracker = Tracker
iou = compute_iou

__all__ = ["Tracker", "IouTracker", "Track", "compute_iou", "iou"]
