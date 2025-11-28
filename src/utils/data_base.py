import sqlite3
import os
from datetime import datetime
from pathlib import Path

# Get the project root directory (2 levels up from this file)
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATABASE_DIR = PROJECT_ROOT / "data" / "database"

# Ensure the database directory exists
DATABASE_DIR.mkdir(parents=True, exist_ok=True)

# Database file paths
USERS_DB = str(DATABASE_DIR / "users.db")
ACTIVITY_DB = str(DATABASE_DIR / "activity.db")

def create_connection(db_file):
    """Creates a database connection to the SQLite database specified by db_file."""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

def create_tables(users_conn, activity_conn):
    """Creates the users table in users_conn and activity_log table in activity_conn."""
    create_users_table_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fio TEXT NOT NULL UNIQUE
    );
    """

    create_activity_log_table_sql = """
    CREATE TABLE IF NOT EXISTS activity_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        activity TEXT NOT NULL,
        timestamp TEXT NOT NULL
    );
    """
    # Note: Foreign Key constraint removed from SQL because tables are in different files.
    # We will manage the relationship logically in the code.

    try:
        if users_conn:
            c = users_conn.cursor()
            c.execute(create_users_table_sql)
        
        if activity_conn:
            c = activity_conn.cursor()
            c.execute(create_activity_log_table_sql)
            
    except sqlite3.Error as e:
        print(e)

def add_user(conn, fio):
    """Adds a new user to the users table."""
    sql = ''' INSERT INTO users(fio)
              VALUES(?) '''
    cur = conn.cursor()
    try:
        cur.execute(sql, (fio,))
        conn.commit()
        return cur.lastrowid
    except sqlite3.IntegrityError:
        # User might already exist, try to fetch
        return get_user_id(conn, fio)
    except sqlite3.Error as e:
        print(e)
        return None

def get_user_id(conn, fio):
    """Gets the user_id for a given FIO."""
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE fio=?", (fio,))
    row = cur.fetchone()
    if row:
        return row[0]
    return None

def log_activity(conn, user_id, activity):
    """Logs an activity for a user."""
    sql = ''' INSERT INTO activity_log(user_id, activity, timestamp)
              VALUES(?,?,?) '''
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur = conn.cursor()
    try:
        cur.execute(sql, (user_id, activity, timestamp))
        conn.commit()
        print(f"Activity logged at {timestamp}")
    except sqlite3.Error as e:
        print(e)
