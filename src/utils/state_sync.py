import json
import logging
import os
import time
from pathlib import Path
from typing import Dict, List

from src.utils.constants import HEARTBEAT_TIMEOUT, STOP_TIMEOUT

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent
SYNC_FILE = PROJECT_ROOT / "data" / "shared_state_sync.json"
SYNC_FILE.parent.mkdir(parents=True, exist_ok=True)


def _read_file() -> Dict:
    """Read sync file with retry logic."""
    max_retries = 3
    retry_delay = 0.01
    
    for attempt in range(max_retries):
        try:
            if not SYNC_FILE.exists():
                return {}
            with open(SYNC_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError, OSError):
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            # Return empty dict on all failures
            return {}
    
    # Fallback (should never reach here)
    return {}


def _write_file(data: Dict):
    """Write sync file with retry logic."""
    max_retries = 5
    retry_delay = 0.05  # 50ms
    
    for attempt in range(max_retries):
        try:
            with open(SYNC_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                f.flush()
                os.fsync(f.fileno())
            return  # Success
        except (IOError, OSError) as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            # Last attempt failed - log but don't crash
            logger.error(f"Error writing sync file after {max_retries} attempts: {e}")


def _create_camera_data(current_time: float) -> Dict:
    """Create initial camera data structure."""
    return {
        'tracks': [],
        'heartbeat': current_time,
        'start_time': current_time,
        'status': 'running'
    }


def register_camera_start(camera_id: str):
    """Register that a camera has started."""
    try:
        data = _read_file()
        current_time = time.time()
        data[camera_id] = _create_camera_data(current_time)
        if 'stop_time' in data.get(camera_id, {}):
            del data[camera_id]['stop_time']
        _write_file(data)
    except Exception as e:
        logger.warning(f"Error registering camera start: {e}")


def register_camera_stop(camera_id: str):
    """Register that a camera has stopped. Clears all data immediately."""
    try:
        data = _read_file()
        current_time = time.time()
        if camera_id in data:
            # Clear all data when camera stops
            data[camera_id]['status'] = 'stopped'
            data[camera_id]['stop_time'] = current_time
            data[camera_id]['tracks'] = []
            # Clear heartbeat to ensure camera is immediately marked as inactive
            data[camera_id]['heartbeat'] = 0
        _write_file(data)
    except Exception as e:
        logger.warning(f"Error registering camera stop: {e}")


def heartbeat_camera(camera_id: str):
    """Send heartbeat from camera."""
    try:
        data = _read_file()
        current_time = time.time()
        
        if camera_id not in data:
            data[camera_id] = _create_camera_data(current_time)
        else:
            data[camera_id]['heartbeat'] = current_time
            data[camera_id]['status'] = 'running'
            if 'stop_time' in data[camera_id]:
                del data[camera_id]['stop_time']
        
        _write_file(data)
    except Exception as e:
        logger.warning(f"Error sending heartbeat: {e}")


def save_camera_tracks(camera_id: str, tracks: List[Dict], timestamp: float):
    """Save camera tracks to sync file."""
    try:
        data = _read_file()
        
        if camera_id not in data:
            data[camera_id] = _create_camera_data(timestamp)
        
        data[camera_id]['tracks'] = tracks
        data[camera_id]['heartbeat'] = timestamp
        data[camera_id]['status'] = 'running'
        if 'stop_time' in data[camera_id]:
            del data[camera_id]['stop_time']
        
        _write_file(data)
    except Exception as e:
        logger.warning(f"Error saving camera tracks: {e}")


def _is_camera_running(camera_data: Dict, current_time: float) -> bool:
    """Check if camera is running based on status, heartbeat, and stop_time."""
    status = camera_data.get('status', 'stopped')
    if status == 'stopped':
        return False
    
    stop_time = camera_data.get('stop_time', 0)
    if stop_time > 0 and (current_time - stop_time < STOP_TIMEOUT):
        return False
    
    heartbeat = camera_data.get('heartbeat', 0)
    heartbeat_age = current_time - heartbeat if heartbeat > 0 else float('inf')
    return heartbeat_age < HEARTBEAT_TIMEOUT


def get_running_camera_ids() -> List[str]:
    """Get list of camera IDs that are currently running."""
    try:
        data = _read_file()
        current_time = time.time()
        return [
            camera_id for camera_id, camera_data in data.items()
            if _is_camera_running(camera_data, current_time)
        ]
    except Exception:
        return []


def get_all_camera_tracks() -> Dict[str, List[Dict]]:
    """Get all camera tracks for running cameras only."""
    try:
        data = _read_file()
        current_time = time.time()
        return {
            camera_id: camera_data.get('tracks', [])
            for camera_id, camera_data in data.items()
            if _is_camera_running(camera_data, current_time)
        }
    except Exception:
        return {}


def _calculate_stats_from_tracks(tracks: List[Dict]) -> Dict[str, int]:
    """Calculate statistics from track list."""
    stats = {'person': 0, 'train': 0, 'total': 0}
    for track in tracks:
        class_name = track.get('class_name', 'unknown')
        if class_name == 'person':
            stats['person'] += 1
        elif class_name == 'train':
            stats['train'] += 1
        stats['total'] += 1
    return stats


def get_camera_stats(camera_id: str) -> Dict[str, int]:
    """Get statistics for a specific camera. Returns zeros if camera is not running."""
    running_cameras = get_running_camera_ids()
    if camera_id not in running_cameras:
        return {'person': 0, 'train': 0, 'total': 0}
    
    all_tracks = get_all_camera_tracks()
    tracks = all_tracks.get(camera_id, [])
    return _calculate_stats_from_tracks(tracks)

