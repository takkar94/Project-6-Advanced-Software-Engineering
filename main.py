import sys
import os
from PySide6 import QtCore, QtWidgets
from modules.systemalerts import get_battery_status
from modules.idle_tracker import get_idle_time
from modules.camera_feed import CameraWidget
from modules.nasa_tlx import TLXForm
from modules.tlx_stats import TLXStatsWidget
from modules.app_tracker import AppTracker  # ✅ New import

# --- Idle Timer Widget ---
class IdleTimerWidget(QtWidgets.QWidget):import sys
import os
from PySide6 import QtCore, QtWidgets
from modules.systemalerts import get_battery_status
from modules.idle_tracker import get_idle_time
from modules.camera_feed import CameraWidget
from modules.nasa_tlx import TLXForm
from modules.tlx_stats import TLXStatsWidget
from modules.app_tracker import AppTracker
from modules.app_usage_summary import AppUsageSummary  # ✅ NEW

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
    def __init__(self):
        super().__init__()

        # Widgets
        self.camera_widget = CameraWidget(self)
        self.idle_timer_widget = IdleTimerWidget()
        self.battery_label = QtWidgets.QLabel("🔋 Battery: --%", alignment=QtCore.Qt.AlignRight)

        self.tlx_button = QtWidgets.QPushButton("Launch NASA TLX")
        self.tlx_button.clicked.connect(self.prompt_tlx)

        self.tlx_stats = TLXStatsWidget()
        self.app_usage_summary = AppUsageSummary()  # ✅ App usage display

        # Layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.camera_widget)
        layout.addWidget(self.tlx_button)
        layout.addWidget(self.battery_label)
        layout.addWidget(self.tlx_stats)
        layout.addWidget(self.app_usage_summary)

        # Battery updater
        self.battery_timer = QtCore.QTimer(self)
        self.battery_timer.timeout.connect(self.update_battery_status)
        self.battery_timer.start(3000)

        self.was_plugged_in = True

        # TLX popup every hour
        self.tlx_timer = QtCore.QTimer(self)
        self.tlx_timer.timeout.connect(self.prompt_tlx)
        self.tlx_timer.start(60 * 60 * 1000)

        # ✅ App usage tracker
        self.app_tracker = AppTracker()
        self.app_tracking_timer = QtCore.QTimer(self)
        self.app_tracking_timer.timeout.connect(self.update_app_usage_display)
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

    def update_app_usage_display(self):
        self.app_tracker.update()
        self.app_usage_summary.refresh_summary()

# --- Run App ---
if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    widget = MyWidget()
    widget.resize(1280, 720)
    widget.show()
    sys.exit(app.exec())

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
    def __init__(self):
        super().__init__()

        # Widgets
        self.camera_widget = CameraWidget(self)
        self.idle_timer_widget = IdleTimerWidget()
        self.battery_label = QtWidgets.QLabel("🔋 Battery: --%", alignment=QtCore.Qt.AlignRight)
        self.tlx_button = QtWidgets.QPushButton("Launch NASA TLX")
        self.tlx_button.clicked.connect(self.prompt_tlx)
        self.tlx_stats = TLXStatsWidget()

        # Layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.camera_widget)
        layout.addWidget(self.tlx_button)
        layout.addWidget(self.battery_label)
        layout.addWidget(self.tlx_stats)

        # Battery updates
        self.battery_timer = QtCore.QTimer(self)
        self.battery_timer.timeout.connect(self.update_battery_status)
        self.battery_timer.start(3000)

        self.was_plugged_in = True

        # TLX auto-popup every hour
        self.tlx_timer = QtCore.QTimer(self)
        self.tlx_timer.timeout.connect(self.prompt_tlx)
        self.tlx_timer.start(60 * 60 * 1000)

        # ✅ App usage tracker
        self.app_tracker = AppTracker()
        self.app_tracking_timer = QtCore.QTimer(self)
        self.app_tracking_timer.timeout.connect(self.app_tracker.update)
        self.app_tracking_timer.start(2000)  # every 2 seconds

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

# --- Run App ---
if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    widget = MyWidget()
    widget.resize(1280, 720)
    widget.show()
    sys.exit(app.exec())
