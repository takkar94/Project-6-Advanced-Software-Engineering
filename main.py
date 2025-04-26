import sys
import os
from PySide6 import QtCore, QtWidgets
from modules.login import LoginDialog
from modules.database.db import init_db, get_db_path
from modules.systemalerts import get_battery_status
from modules.idle_tracker import get_idle_time
from modules.camera_feed import CameraWidget
from modules.nasa_tlx import TLXForm
from modules.tlx_stats import TLXStatsWidget
from modules.app_tracker import AppTracker
from modules.app_usage_summary import AppUsageSummary
from modules.frustration_skill import FrustrationDistractionDialog

# --- Idle Timer Widget ---
class IdleTimerWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setFixedSize(300, 100)

        self.timer_label = QtWidgets.QLabel("Idle Time: 0s", self)
        self.timer_label.setAlignment(QtCore.Qt.AlignCenter)
        self.timer_label.setStyleSheet("""
            background: red;
            color: white;
            font-size: 20px;
            font-weight: bold;
            padding: 15px;
            border-radius: 15px;
        """)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.timer_label)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_idle_timer)
        self.timer.start(1000)
        self.hide()

    def update_idle_timer(self):
        idle_time = int(get_idle_time())
        if idle_time > 30:
            self.timer_label.setText(f"Idle Time: {idle_time}s")
            self.show_timer()
        else:
            self.hide()

    def show_timer(self):
        screen_geometry = QtWidgets.QApplication.primaryScreen().availableGeometry()
        self.move(screen_geometry.width() - 320, 50)
        self.show()


# --- Main Application Widget ---
class MyWidget(QtWidgets.QWidget):
    def __init__(self, user):
        super().__init__()
        print("🔧 Initializing Main Widget...")

        self.user = user
        self.user_id = user["id"]

        self.camera_widget = CameraWidget(self)
        self.idle_timer_widget = IdleTimerWidget()
        self.battery_label = QtWidgets.QLabel("🔋 Battery: --%", alignment=QtCore.Qt.AlignRight)

        self.tlx_button = QtWidgets.QPushButton("Launch NASA TLX")
        self.tlx_button.clicked.connect(self.prompt_tlx)
        self.tlx_button.setFixedWidth(180)
        self.tlx_button.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #005f99;
            }
        """)

        self.notify_button = QtWidgets.QPushButton("show notification")
        self.notify_button.clicked.connect(self.show_notification)

        self.tlx_stats = TLXStatsWidget()
        self.app_usage_summary = AppUsageSummary()

        # Layout
        main_layout = QtWidgets.QHBoxLayout(self)

        # Left
        left_layout = QtWidgets.QVBoxLayout()
        left_layout.addWidget(self.camera_widget)
        left_layout.addWidget(self.notify_button)

        # Right
        right_layout = QtWidgets.QVBoxLayout()
        battery_layout = QtWidgets.QHBoxLayout()
        battery_layout.addStretch()
        battery_layout.addWidget(self.battery_label)

        right_layout.addLayout(battery_layout)
        right_layout.addWidget(self.tlx_button, alignment=QtCore.Qt.AlignLeft)
        right_layout.addSpacing(10)
        right_layout.addWidget(self.tlx_stats)
        right_layout.addWidget(self.app_usage_summary)
        right_layout.addStretch()

        main_layout.addLayout(left_layout, stretch=2)
        main_layout.addLayout(right_layout, stretch=1)

        print("✅ Layout initialized.")

        # Battery Timer
        self.battery_timer = QtCore.QTimer(self)
        self.battery_timer.timeout.connect(self.update_battery_status)
        self.battery_timer.start(3000)
        self.was_plugged_in = True

        # TLX auto timer
        self.tlx_timer = QtCore.QTimer(self)
        self.tlx_timer.timeout.connect(self.prompt_tlx)
        self.tlx_timer.start(60 * 60 * 1000)

        # App Usage Tracker
        self.app_tracker = AppTracker()
        self.app_tracking_timer = QtCore.QTimer(self)
        self.app_tracking_timer.timeout.connect(self.app_tracker.update)
        self.app_tracker.app_switched.connect(self.app_usage_summary.refresh_summary)
        self.app_tracking_timer.start(2000)

    @QtCore.Slot()
    def update_battery_status(self):
        percentage, is_plugged_in = get_battery_status()
        self.battery_label.setText(f"🔋 Battery: {percentage}%")
        if not is_plugged_in and self.was_plugged_in:
            QtWidgets.QMessageBox.warning(self, "⚠️ Power Alert", "Device is not charging!")
        self.was_plugged_in = is_plugged_in

    def prompt_tlx(self):
        print("📋 Prompting TLX form...")
        form = TLXForm()
        if form.exec() == QtWidgets.QDialog.Accepted:
            result = form.get_results()
            print("🧪 TLX Form Results:", result)

            # Optional: Trigger Frustration Distraction Dialog
            if result.get("Frustration", 0) >= 70 or result.get("frustration", 0) >= 70:
                dialog = FrustrationDistractionDialog()
                dialog.exec()

            # Save TLX to Database
            save_tlx_result_to_db(result, self.user_id)

            # Refresh Stats
            self.tlx_stats.refresh_stats()

    def show_notification(self):
        print("📢 Show notification clicked.")
        # subprocess.Popen([sys.executable, "tempCodeRunnerFile.py"])  # Temporarily disabled


# ✅ Helper Function to Save TLX Result to DB
def save_tlx_result_to_db(result: dict, user_id: int):
    try:
        import sqlite3

        # Safe fetching from result
        mental = result.get("Mental") or result.get("mental", 0)
        physical = result.get("Physical") or result.get("physical", 0)
        temporal = result.get("Temporal") or result.get("temporal", 0)
        performance = result.get("Performance") or result.get("performance", 0)
        effort = result.get("Effort") or result.get("effort", 0)
        frustration = result.get("Frustration") or result.get("frustration", 0)

        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO tlx_entries (user_id, mental, physical, temporal, performance, effort, frustration)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            mental,
            physical,
            temporal,
            performance,
            effort,
            frustration
        ))

        conn.commit()
        conn.close()
        print("✅ TLX result successfully saved to database.")
    except Exception as e:
        print(f"❌ Failed to save TLX result to database: {e}")


# --- Entry Point ---
if __name__ == "__main__":
    try:
        print("🚀 Starting application...")
        init_db()
        print("📦 Database initialized.")

        app = QtWidgets.QApplication([])

        login = LoginDialog()
        print("🔑 Launching login dialog...")
        if login.exec() == QtWidgets.QDialog.Accepted:
            user = login.get_user_info()
            print(f"✅ Logged in as {user['name']} ({user['role']})")

            widget = MyWidget(user)
            widget.resize(1280, 720)
            widget.show()
            sys.exit(app.exec())
        else:
            print("❌ Login cancelled.")
            sys.exit()
    except Exception as e:
        print(f"🔥 Crash occurred: {e}")
