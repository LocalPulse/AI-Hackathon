import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from contextlib import contextmanager
import threading

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DATABASE_DIR = PROJECT_ROOT / "data" / "database"
DATABASE_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DB = str(DATABASE_DIR / "logs.db")

_db_lock = threading.Lock()


@contextmanager
def _get_connection():
    """Context manager for database connections."""
    conn = None
    try:
        conn = sqlite3.connect(LOGS_DB, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        yield conn
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        raise
    finally:
        if conn:
            conn.close()


def init_logs_db():
    """Initialize logs database with required table."""
    sql = """
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        track_id INTEGER NOT NULL,
        class TEXT NOT NULL,
        activity TEXT NOT NULL,
        confidence REAL NOT NULL,
        timestamp TEXT NOT NULL,
        camera_id TEXT
    );
    """
    
    with _db_lock:
        try:
            with _get_connection() as conn:
                conn.execute(sql)
                conn.commit()
                
                cursor = conn.cursor()
                cursor.execute("PRAGMA table_info(logs)")
                columns = [row[1] for row in cursor.fetchall()]
                
                if 'camera_id' not in columns:
                    logger.info("Adding camera_id column to logs table")
                    conn.execute("ALTER TABLE logs ADD COLUMN camera_id TEXT")
                    conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error initializing logs DB: {e}")


def log_activity(
    track_id: int,
    class_name: str,
    activity: str,
    confidence: float,
    timestamp: Optional[str] = None,
    camera_id: Optional[str] = None
):
    """
    Log an activity to the database.
    
    Args:
        track_id: Unique track ID
        class_name: Object class (person, train, etc.)
        activity: Activity label (standing, moving, stopped)
        confidence: Confidence score (0.0 - 1.0)
        timestamp: Optional timestamp (defaults to current time)
        camera_id: Optional camera identifier
    """
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    sql = """
    INSERT INTO logs (track_id, class, activity, confidence, timestamp, camera_id)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    
    with _db_lock:
        try:
            with _get_connection() as conn:
                conn.execute(sql, (track_id, class_name, activity, confidence, timestamp, camera_id))
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error logging activity: {e}")


def _build_filter_query(
    class_filter: Optional[str],
    activity_filter: Optional[str],
    camera_id: Optional[str] = None
) -> tuple[str, List]:
    """Build SQL query with optional filters."""
    sql = "SELECT * FROM logs WHERE 1=1"
    params = []
    
    if class_filter:
        sql += " AND class = ?"
        params.append(class_filter)
    
    if activity_filter:
        sql += " AND activity = ?"
        params.append(activity_filter)
    
    if camera_id:
        sql += " AND camera_id = ?"
        params.append(camera_id)
    
    return sql, params


def get_logs(
    limit: int = 100,
    offset: int = 0,
    class_filter: Optional[str] = None,
    activity_filter: Optional[str] = None,
    camera_id: Optional[str] = None
) -> List[Dict]:
    """
    Retrieve logs from database.
    
    Args:
        limit: Maximum number of records to return
        offset: Number of records to skip
        class_filter: Filter by class name (optional)
        activity_filter: Filter by activity (optional)
        camera_id: Filter by camera ID (optional)
    
    Returns:
        List of log dictionaries
    """
    sql, params = _build_filter_query(class_filter, activity_filter, camera_id)
    sql += " ORDER BY timestamp DESC, id DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    with _db_lock:
        try:
            with _get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, params)
                rows = cursor.fetchall()
                return _rows_to_dicts(rows)
        except sqlite3.Error as e:
            logger.error(f"Error retrieving logs: {e}")
            return []


def _rows_to_dicts(rows: List) -> List[Dict]:
    """Convert SQLite rows to dictionaries."""
    return [
        {
            "id": row["id"],
            "track_id": row["track_id"],
            "class": row["class"],
            "activity": row["activity"],
            "confidence": row["confidence"],
            "timestamp": row["timestamp"],
            "camera_id": row["camera_id"] if "camera_id" in row.keys() else None
        }
        for row in rows
    ]


def get_log_count(
    class_filter: Optional[str] = None,
    activity_filter: Optional[str] = None,
    camera_id: Optional[str] = None
) -> int:
    """Get total count of logs with optional filters."""
    sql, params = _build_filter_query(class_filter, activity_filter, camera_id)
    sql = sql.replace("SELECT *", "SELECT COUNT(*) as count")
    
    with _db_lock:
        try:
            with _get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, params)
                row = cursor.fetchone()
                return row["count"] if row else 0
        except sqlite3.Error as e:
            logger.error(f"Error getting log count: {e}")
            return 0


def get_active_camera_ids(seconds_threshold: int = 300) -> List[str]:
    """
    Get list of camera IDs that have recent activity in the database.
    
    Args:
        seconds_threshold: Maximum seconds since last activity to consider camera active
    
    Returns:
        List of camera IDs with recent activity
    """
    threshold_time = (datetime.now() - timedelta(seconds=seconds_threshold)).strftime("%Y-%m-%d %H:%M:%S")
    
    sql = """
    SELECT DISTINCT camera_id 
    FROM logs 
    WHERE camera_id IS NOT NULL 
    AND timestamp > ?
    ORDER BY camera_id
    """
    
    with _db_lock:
        try:
            with _get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (threshold_time,))
                rows = cursor.fetchall()
                return [row["camera_id"] for row in rows if row["camera_id"]]
        except sqlite3.Error as e:
            logger.error(f"Error getting active camera IDs: {e}")
            return []


def get_camera_stats_from_db(camera_id: str, seconds_threshold: int = 300) -> Dict[str, int]:
    """
    Get statistics for a camera from database (recent activity).
    
    Args:
        camera_id: Camera identifier
        seconds_threshold: Maximum seconds since last activity
    
    Returns:
        Dictionary with counts: {'person': 0, 'train': 0, 'total': 0}
    """
    threshold_time = (datetime.now() - timedelta(seconds=seconds_threshold)).strftime("%Y-%m-%d %H:%M:%S")
    
    sql = """
    SELECT class, COUNT(*) as count
    FROM logs
    WHERE camera_id = ? AND timestamp > ?
    GROUP BY class
    """
    
    stats = {'person': 0, 'train': 0, 'total': 0}
    
    with _db_lock:
        try:
            with _get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (camera_id, threshold_time))
                rows = cursor.fetchall()
                
                for row in rows:
                    class_name = row["class"]
                    count = row["count"]
                    if class_name in stats:
                        stats[class_name] = count
                    stats['total'] += count
        except sqlite3.Error as e:
            logger.error(f"Error getting camera stats from DB: {e}")
    
    return stats


# Initialize logs database on module import
init_logs_db()
