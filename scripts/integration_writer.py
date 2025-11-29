#!/usr/bin/env python3
"""
Simple integration writer: simulates AI video processing by writing movement data
to a SQLite database table periodically.
Usage:
  python3 scripts/integration_writer.py --db data/raw/test_data.db --table movement --interval 2 --count 30
"""
import argparse
import sqlite3
import time
import random
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument('--db', required=False, default='data/raw/test_data.db')
parser.add_argument('--table', required=False, default='movement')
parser.add_argument('--interval', type=float, default=2.0, help='Seconds between inserts')
parser.add_argument('--count', type=int, default=30, help='Number of rows to insert (0 = infinite)')
args = parser.parse_args()

DB = args.db
TABLE = args.table
INTERVAL = args.interval
COUNT = args.count

print(f"Integration writer starting: db={DB}, table={TABLE}, interval={INTERVAL}s, count={COUNT}")

conn = sqlite3.connect(DB)
cur = conn.cursor()
# Create table if not exists
cur.execute(f"""
CREATE TABLE IF NOT EXISTS {TABLE} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT,
    worker TEXT,
    x REAL,
    y REAL,
    speed REAL
)
""")
conn.commit()

workers = ['Worker_1','Worker_2','Worker_3','Worker_4','Worker_5']

inserted = 0
try:
    while True:
        ts = datetime.utcnow().isoformat()
        worker = random.choice(workers)
        x = random.uniform(0, 100)
        y = random.uniform(0, 100)
        speed = random.uniform(0, 5)
        cur.execute(f"INSERT INTO {TABLE} (ts, worker, x, y, speed) VALUES (?, ?, ?, ?, ?)", (ts, worker, x, y, speed))
        conn.commit()
        inserted += 1
        print(f"[{inserted}] inserted: {ts} {worker} x={x:.1f} y={y:.1f} speed={speed:.2f}")
        if COUNT > 0 and inserted >= COUNT:
            break
        time.sleep(INTERVAL)
except KeyboardInterrupt:
    print('Interrupted by user')
finally:
    conn.close()
    print('Writer finished')
