import pandas as pd
import os
from datetime import datetime

class DataManager:
    def __init__(self, file_path="data/logs.csv"):
        self.file_path = file_path
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Creates the data directory and file if they don't exist."""
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            # Create empty dataframe with columns
            df = pd.DataFrame(columns=["worker_id", "timestamp", "action_name"])
            df.to_csv(self.file_path, index=False)

    def log_action(self, worker_id, action_name):
        """Appends a new action to the log file."""
        timestamp = datetime.now()
        new_row = pd.DataFrame({
            "worker_id": [worker_id],
            "timestamp": [timestamp],
            "action_name": [action_name]
        })
        # Append to CSV without reading the whole file if possible, 
        # but for simplicity and safety with headers, we'll use mode='a'
        new_row.to_csv(self.file_path, mode='a', header=False, index=False)

    def get_data(self):
        """Reads the log file and returns a DataFrame."""
        try:
            df = pd.read_csv(self.file_path)
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
        except Exception as e:
            print(f"Error reading data: {e}")
            return pd.DataFrame(columns=["worker_id", "timestamp", "action_name"])
