# Logging intervals
LOG_INTERVAL = 5.0  # seconds between progress logs
HEARTBEAT_INTERVAL = 2.0  # seconds between heartbeats
PERIODIC_LOG_INTERVAL = 30.0  # seconds between periodic activity logs

# State synchronization timeouts
HEARTBEAT_TIMEOUT = 60.0  # seconds before camera is considered inactive
STOP_TIMEOUT = 300.0  # 5 minutes - timeout after camera stop

# Default camera ID
DEFAULT_CAMERA_ID = 'default'

# Tracker defaults (used as fallback when config doesn't provide values)
DEFAULT_IOU_THRESHOLD = 0.2
DEFAULT_MAX_LOST = 45
DEFAULT_ACTIVITY_WINDOW = 30
DEFAULT_PERSON_SPEED_THRESHOLD = 0.5
DEFAULT_VEHICLE_DISPLACEMENT_THRESHOLD = 10.0
DEFAULT_VEHICLE_MIN_HISTORY = 5

# UI constants
WINDOW_NAME = "AI-Hackathon"
QUIT_KEYS = (ord("q"), 27)  # 'q' key and ESC key

