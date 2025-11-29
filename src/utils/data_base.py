import sqlite3
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import threading

# Get the project root directory (2 levels up from this file)
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATABASE_DIR = PROJECT_ROOT / "data" / "database"

# Ensure the database directory exists
DATABASE_DIR.mkdir(parents=True, exist_ok=True)

# Database file paths
DETECTIONS_DB = str(DATABASE_DIR / "detections.db")

# Thread lock for database operations
_db_lock = threading.Lock()


def create_connection(db_file):
    """Creates a database connection to the SQLite database specified by db_file."""
    conn = None
    try:
        conn = sqlite3.connect(db_file, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn


def init_detections_db():
    """Initialize detections database with required table."""
    create_detections_table_sql = """
    CREATE TABLE IF NOT EXISTS detections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        track_id INTEGER NOT NULL,
        class TEXT NOT NULL,
        activity TEXT NOT NULL,
        confidence REAL NOT NULL,
        timestamp TEXT NOT NULL
    );
    """
    
    try:
        conn = create_connection(DETECTIONS_DB)
        if conn:
            cursor = conn.cursor()
            cursor.execute(create_detections_table_sql)
            conn.commit()
            conn.close()
    except sqlite3.Error as e:
        print(f"Error initializing detections DB: {e}")


def log_detection(track_id: int, class_name: str, activity: str, confidence: float, timestamp: Optional[str] = None):
    """
    Log a detection to the database.
    
    Args:
        track_id: Unique track ID
        class_name: Object class (person, train, etc.)
        activity: Activity label (standing, moving, stopped)
        confidence: Confidence score (0.0 - 1.0)
        timestamp: Optional timestamp (defaults to current time)
    """
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    sql = """
    INSERT INTO detections (track_id, class, activity, confidence, timestamp)
    VALUES (?, ?, ?, ?, ?)
    """
    
    with _db_lock:
        try:
            conn = create_connection(DETECTIONS_DB)
            if conn:
                cursor = conn.cursor()
                cursor.execute(sql, (track_id, class_name, activity, confidence, timestamp))
                conn.commit()
                conn.close()
        except sqlite3.Error as e:
            print(f"Error logging detection: {e}")


def get_detections(limit: int = 100, offset: int = 0, class_filter: Optional[str] = None, 
                   activity_filter: Optional[str] = None) -> List[Dict]:
    """
    Retrieve detections from database.
    
    Args:
        limit: Maximum number of records to return
        offset: Number of records to skip
        class_filter: Filter by class name (optional)
        activity_filter: Filter by activity (optional)
    
    Returns:
        List of detection dictionaries
    """
    sql = "SELECT * FROM detections WHERE 1=1"
    params = []
    
    if class_filter:
        sql += " AND class = ?"
        params.append(class_filter)
    
    if activity_filter:
        sql += " AND activity = ?"
        params.append(activity_filter)
    
    sql += " ORDER BY timestamp DESC, id DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    with _db_lock:
        try:
            conn = create_connection(DETECTIONS_DB)
            if conn:
                cursor = conn.cursor()
                cursor.execute(sql, params)
                rows = cursor.fetchall()
                conn.close()
                
                return [
                    {
                        "id": row["id"],
                        "track_id": row["track_id"],
                        "class": row["class"],
                        "activity": row["activity"],
                        "confidence": row["confidence"],
                        "timestamp": row["timestamp"]
                    }
                    for row in rows
                ]
        except sqlite3.Error as e:
            print(f"Error retrieving detections: {e}")
    
    return []


def get_detection_count(class_filter: Optional[str] = None, activity_filter: Optional[str] = None) -> int:
    """Get total count of detections with optional filters."""
    sql = "SELECT COUNT(*) as count FROM detections WHERE 1=1"
    params = []
    
    if class_filter:
        sql += " AND class = ?"
        params.append(class_filter)
    
    if activity_filter:
        sql += " AND activity = ?"
        params.append(activity_filter)
    
    with _db_lock:
        try:
            conn = create_connection(DETECTIONS_DB)
            if conn:
                cursor = conn.cursor()
                cursor.execute(sql, params)
                row = cursor.fetchone()
                conn.close()
                return row["count"] if row else 0
        except sqlite3.Error as e:
            print(f"Error getting detection count: {e}")
    
    return 0


# Initialize detections database on module import
init_detections_db()
