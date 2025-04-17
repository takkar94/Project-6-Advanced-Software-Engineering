import sys
import os
from PySide6 import QtCore, QtWidgets
from modules.login import LoginDialog
from modules.database.db import init_db
from modules.systemalerts import get_battery_status
from modules.idle_tracker import get_idle_time
from modules.camera_feed import CameraWidget
from modules.nasa_tlx import TLXForm
from modules.tlx_stats import TLXStatsWidget
from modules.app_tracker import AppTracker
from modules.app_usage_summary import AppUsageSummary

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
        self.user = user  # Store logged-in user info
        self.user_id = user["id"]

        # --- Widgets ---
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

        self.tlx_stats = TLXStatsWidget()
        self.app_usage_summary = AppUsageSummary()

        # --- Layout Setup ---
        main_layout = QtWidgets.QHBoxLayout(self)

        # Left panel (camera)
        left_layout = QtWidgets.QVBoxLayout()
        left_layout.addWidget(self.camera_widget)

        # Right panel (battery, TLX button, stats)
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

        # --- Battery Timer ---
        self.battery_timer = QtCore.QTimer(self)
        self.battery_timer.timeout.connect(self.update_battery_status)
        self.battery_timer.start(3000)

        self.was_plugged_in = True

        # --- NASA TLX Auto Prompt Timer ---
        self.tlx_timer = QtCore.QTimer(self)
        self.tlx_timer.timeout.connect(self.prompt_tlx)
        self.tlx_timer.start(60 * 60 * 1000)

        # --- App Usage Tracker ---
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
        form = TLXForm()
        if form.exec() == QtWidgets.QDialog.Accepted:
            result = form.get_results()

            file_exists = os.path.isfile("tlx_results.csv")
            with open("tlx_results.csv", "a", newline='') as f:
                headers = ["Mental", "Physical", "Temporal", "Performance", "Effort", "Frustration"]
                import csv
                writer = csv.DictWriter(f, fieldnames=headers)
                if not file_exists:
                    writer.writeheader()
                writer.writerow({key: result.get(key, "") for key in headers})

            self.tlx_stats.refresh_stats()

# --- App Entry Point ---
if __name__ == "__main__":
    init_db()

    app = QtWidgets.QApplication([])

    login = LoginDialog()
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
