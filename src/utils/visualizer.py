from __future__ import annotations

from typing import List, Tuple
import cv2
import numpy as np


ACTIVITY_COLORS = {
    "standing": (0, 255, 0),
    "moving": (0, 200, 255),
    "stopped": (128, 128, 128),
}


def get_track_color(track_id: int) -> Tuple[int, int, int]:
    rng = np.random.RandomState(track_id)
    return tuple(int(rng.randint(60, 220)) for _ in range(3))


def get_activity_color(activity: str) -> Tuple[int, int, int]:
    return ACTIVITY_COLORS.get(activity, (100, 100, 100))


def fade_color(color: Tuple, factor: float) -> Tuple[int, int, int]:
    return tuple(int(c * factor) for c in color)


def draw_dashed_rect(frame: np.ndarray, pt1: Tuple, pt2: Tuple, color: Tuple, thickness: int = 2, dash_len: int = 10):
    x1, y1 = pt1
    x2, y2 = pt2
    
    for x in range(x1, x2, dash_len * 2):
        cv2.line(frame, (x, y1), (min(x + dash_len, x2), y1), color, thickness)
    for x in range(x1, x2, dash_len * 2):
        cv2.line(frame, (x, y2), (min(x + dash_len, x2), y2), color, thickness)
    for y in range(y1, y2, dash_len * 2):
        cv2.line(frame, (x1, y), (x1, min(y + dash_len, y2)), color, thickness)
    for y in range(y1, y2, dash_len * 2):
        cv2.line(frame, (x2, y), (x2, min(y + dash_len, y2)), color, thickness)


def draw_box(frame: np.ndarray, bbox: Tuple, label: str, color: Tuple, dashed: bool = False):
    x1, y1, x2, y2 = map(int, bbox)
    
    if dashed:
        draw_dashed_rect(frame, (x1, y1), (x2, y2), color, 2)
    else:
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
    
    if label:
        sz, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(frame, (x1, y1 - sz[1] - 6), (x1 + sz[0] + 6, y1), color, -1)
        cv2.putText(frame, label, (x1 + 3, y1 - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)


def draw_activity_badge(frame: np.ndarray, bbox: Tuple, text: str, color: Tuple):
    x1, _, _, y2 = map(int, bbox)
    sz, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
    cv2.rectangle(frame, (x1, y2 + 5), (x1 + sz[0] + 10, y2 + sz[1] + 13), color, -1)
    cv2.putText(frame, text, (x1 + 5, y2 + sz[1] + 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)


def draw_trail(frame: np.ndarray, history: List[Tuple], color: Tuple):
    if len(history) < 2:
        return
    
    pts = [(int(x), int(y)) for x, y in history]
    
    for i in range(1, len(pts)):
        alpha = i / len(pts)
        c = tuple(int(v * alpha) for v in color)
        cv2.line(frame, pts[i-1], pts[i], c, 2)
    
    cv2.circle(frame, pts[-1], 4, color, -1)


def draw_tracks(frame: np.ndarray, tracks: List, show_lost: bool = True):
    for track in tracks:
        cls_name = getattr(track, "cls_name", None)
        activity = getattr(track, "activity", None)
        lost_frames = getattr(track, "lost_frames", 0)
        
        is_lost = lost_frames > 0
        
        if is_lost:
            if not show_lost or lost_frames > 30:
                continue
        
        color = get_track_color(track.id)
        if activity and cls_name == "person":
            color = get_activity_color(activity)
        
        if is_lost:
            color = fade_color(color, 0.5)
        
        label = f"{cls_name or track.cls} #{track.id}"
        if not is_lost:
            label += f" {track.score:.2f}"
        else:
            label += " (lost)"
        
        clothing = getattr(track, "clothing", None)
        if clothing and not is_lost:
            label += f" PPE:{clothing}"
        
        draw_box(frame, track.bbox, label, color, dashed=is_lost)
        
        if activity and not is_lost:
            conf = getattr(track, "activity_conf", 0.0)
            draw_activity_badge(frame, track.bbox, f"{activity} {conf:.0%}", get_activity_color(activity))
        
        history = getattr(track, "history", [])
        draw_trail(frame, history, color)


__all__ = ["draw_tracks", "draw_box"]
