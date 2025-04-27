from PySide6.QtCore import QObject, Signal
import time
import os
from datetime import datetime
import sqlite3
from modules.database.db import get_db_path

class AppTracker(QObject):
    app_switched = Signal()  # ✅ Signal to notify app change

    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.current_app = None
        self.start_time = datetime.now()

    def get_active_window_title(self):
        try:
            import win32gui
            return win32gui.GetWindowText(win32gui.GetForegroundWindow())
        except:
            return "Unknown"

    def update(self):
        active_app = self.get_active_window_title()

        if active_app != self.current_app:
            now = datetime.now()

            if self.current_app is not None:
                duration = int((now - self.start_time).total_seconds())
                self.save_to_db(self.current_app, self.start_time, now, duration)

            self.current_app = active_app
            self.start_time = now

            self.app_switched.emit()

    def save_to_db(self, app_name, start_time, end_time, duration):
        try:
            db_path = get_db_path()
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO app_usage (user_id, app, start_time, end_time, duration)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                self.user_id,
                app_name,
                start_time.strftime("%H:%M:%S"),
                end_time.strftime("%H:%M:%S"),
                duration
            ))

            conn.commit()
            conn.close()
            print(f"✅ App Usage Logged: {app_name}, Duration: {duration}s")
        except Exception as e:
            print(f"❌ Failed to save app usage to DB: {e}")
