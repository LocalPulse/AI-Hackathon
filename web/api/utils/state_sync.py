"""
Compatibility layer for state synchronization.
This module re-exports functions from src.utils.state_sync for backward compatibility.
"""

# Re-export all functions from the common module
from src.utils.state_sync import (
    register_camera_start,
    register_camera_stop,
    heartbeat_camera,
    save_camera_tracks,
    get_running_camera_ids,
    get_all_camera_tracks,
    get_camera_stats,
)

__all__ = [
    'register_camera_start',
    'register_camera_stop',
    'heartbeat_camera',
    'save_camera_tracks',
    'get_running_camera_ids',
    'get_all_camera_tracks',
    'get_camera_stats',
]
