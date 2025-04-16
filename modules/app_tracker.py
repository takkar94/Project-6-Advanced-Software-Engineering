import time
import csv
import os
from datetime import datetime
import win32gui  # Requires pywin32

class AppTracker:
    def __init__(self, log_file="app_usage_log.csv"):
        self.log_file = log_file
        self.current_app = None
        self.start_time = datetime.now()

        if not os.path.exists(self.log_file):
            with open(self.log_file, "w", newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["App", "Start Time", "End Time", "Duration (s)"])

    def get_active_window_title(self):
        try:
            return win32gui.GetWindowText(win32gui.GetForegroundWindow())
        except:
            return "Unknown"

    def update(self):
        active_app = self.get_active_window_title()

        if active_app != self.current_app:
            now = datetime.now()

            if self.current_app is not None:
                duration = (now - self.start_time).total_seconds()
                with open(self.log_file, "a", newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        self.current_app,
                        self.start_time.strftime("%H:%M:%S"),
                        now.strftime("%H:%M:%S"),
                        round(duration)
                    ])

            self.current_app = active_app
            self.start_time = now
