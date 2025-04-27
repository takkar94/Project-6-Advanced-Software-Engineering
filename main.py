import sys
import os
from PySide6 import QtCore, QtWidgets
from modules.login import LoginDialog
from modules.database.db import init_db, get_db_path, save_tlx_result_to_db, save_usability_feedback
from modules.systemalerts import get_battery_status
from modules.idle_tracker import get_idle_time
from modules.camera_feed import CameraWidget
from modules.nasa_tlx import TLXForm
from modules.tlx_stats import TLXStatsWidget
from modules.app_tracker import AppTracker
from modules.app_usage_summary import AppUsageSummary
from modules.frustration_skill import FrustrationDistractionDialog
from modules.system_usability_skill import SystemUsabilityDialog

# --- Manager Conversation Popup ---
class ManagerConversationPopup(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manager Conversation Check")
        self.setMinimumSize(300, 150)

        layout = QtWidgets.QVBoxLayout(self)

        label = QtWidgets.QLabel("Are you currently in conversation with the manager?")
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setWordWrap(True)

        button_layout = QtWidgets.QHBoxLayout()
        yes_button = QtWidgets.QPushButton("Yes")
        no_button = QtWidgets.QPushButton("No")

        yes_button.clicked.connect(self.accept)
        no_button.clicked.connect(self.reject)

        button_layout.addWidget(yes_button)
        button_layout.addWidget(no_button)

        layout.addWidget(label)
        layout.addLayout(button_layout)

# --- Idle Timer Widget ---
class IdleTimerWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
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

        if idle_time >= 60:
            self.prompt_manager_conversation()

    def prompt_manager_conversation(self):
        popup = ManagerConversationPopup()
        if popup.exec() == QtWidgets.QDialog.Accepted:
            print("User indicated they are talking to the manager.")
        else:
            print("User indicated they are not talking to the manager.")

    def show_timer(self):
        screen_geometry = QtWidgets.QApplication.primaryScreen().availableGeometry()
        self.move(screen_geometry.width() - 320, 50)
        self.show()

# --- Main Application Widget ---
class MyWidget(QtWidgets.QWidget):
    def __init__(self, user):
        super().__init__()
        print("Initializing Main Widget...")

        self.user = user
        self.user_id = user["id"]
        self.user_role = user["role"]

        self.camera_widget = CameraWidget(self)
        self.idle_timer_widget = IdleTimerWidget()
        self.battery_label = QtWidgets.QLabel("Battery: --%", alignment=QtCore.Qt.AlignRight)

        self.tlx_button = QtWidgets.QPushButton("Launch NASA TLX")
        self.tlx_button.clicked.connect(self.prompt_tlx)
        self.tlx_button.setFixedWidth(180)

        self.notify_button = QtWidgets.QPushButton("Show Notification")
        self.notify_button.clicked.connect(self.show_notification)

        self.tlx_stats = TLXStatsWidget(self.user_id, self.user_role)
        self.app_usage_summary = AppUsageSummary(self.user_id)

        # Layout
        main_layout = QtWidgets.QHBoxLayout(self)

        # Group Boxes
        self.camera_group = QtWidgets.QGroupBox("Camera Feed")
        camera_layout = QtWidgets.QVBoxLayout()
        camera_layout.addWidget(self.camera_widget)
        self.camera_group.setLayout(camera_layout)

        self.app_usage_group = QtWidgets.QGroupBox("Application Usage Summary")
        app_usage_layout = QtWidgets.QVBoxLayout()
        app_usage_layout.addWidget(self.app_usage_summary)
        self.app_usage_group.setLayout(app_usage_layout)

        self.tlx_stats_group = QtWidgets.QGroupBox("NASA TLX Statistics")
        tlx_layout = QtWidgets.QVBoxLayout()
        tlx_layout.addWidget(self.tlx_stats)
        self.tlx_stats_group.setLayout(tlx_layout)

        # Left Layout
        left_layout = QtWidgets.QVBoxLayout()
        left_layout.addWidget(self.camera_group)
        left_layout.addWidget(self.notify_button)

        # Right Layout
        right_layout = QtWidgets.QVBoxLayout()
        battery_layout = QtWidgets.QHBoxLayout()
        battery_layout.addStretch()
        battery_layout.addWidget(self.battery_label)

        right_layout.addLayout(battery_layout)
        right_layout.addWidget(self.tlx_button)
        right_layout.addWidget(self.tlx_stats_group)
        right_layout.addWidget(self.app_usage_group)
        right_layout.addStretch()

        main_layout.addLayout(left_layout, stretch=2)
        main_layout.addLayout(right_layout, stretch=1)

        print("Layout initialized.")

        # Battery Timer
        self.battery_timer = QtCore.QTimer(self)
        self.battery_timer.timeout.connect(self.update_battery_status)
        self.battery_timer.start(3000)
        self.was_plugged_in = True

        # TLX Auto Timer
        self.tlx_timer = QtCore.QTimer(self)
        self.tlx_timer.timeout.connect(self.prompt_tlx)
        self.tlx_timer.start(60 * 60 * 1000)

        # App Usage Tracker
        self.app_tracker = AppTracker(self.user_id)
        self.app_tracking_timer = QtCore.QTimer(self)
        self.app_tracking_timer.timeout.connect(self.app_tracker.update)
        self.app_tracker.app_switched.connect(self.app_usage_summary.refresh_summary)
        self.app_tracking_timer.start(2000)

    @QtCore.Slot()
    def update_battery_status(self):
        percentage, is_plugged_in = get_battery_status()
        self.battery_label.setText(f"Battery: {percentage}%")
        if not is_plugged_in and self.was_plugged_in:
            QtWidgets.QMessageBox.warning(self, "Power Alert", "Device is not charging.")
        self.was_plugged_in = is_plugged_in

    def prompt_tlx(self):
        print("Prompting TLX form...")
        form = TLXForm()
        if form.exec() == QtWidgets.QDialog.Accepted:
            result = form.get_results()
            print("TLX Form Results:", result)

            if result.get("Frustration", 0) >= 70 or result.get("frustration", 0) >= 70:
                dialog = FrustrationDistractionDialog()
                dialog.exec()

            save_tlx_result_to_db(result, self.user_id)
            self.tlx_stats.refresh_stats()

            usability_dialog = SystemUsabilityDialog()
            if usability_dialog.exec() == QtWidgets.QDialog.Accepted:
                usability_score = usability_dialog.get_score()
                save_usability_feedback(self.user_id, usability_score)

    def show_notification(self):
        QtWidgets.QMessageBox.information(self, "Notification", "Test Notification Triggered.")

# --- Entry Point ---
if __name__ == "__main__":
    try:
        print("Starting application...")
        init_db()
        print("Database initialized.")

        app = QtWidgets.QApplication([])

        # Load external stylesheet from assets/css/style.qss
        style_path = os.path.join(os.path.dirname(__file__), "assets", "css", "style.qss")
        if os.path.exists(style_path):
            with open(style_path, "r") as f:
                app.setStyleSheet(f.read())
        else:
            print("Warning: style.qss not found!")

        login = LoginDialog()
        print("Launching login dialog...")
        if login.exec() == QtWidgets.QDialog.Accepted:
            user = login.get_user_info()
            print(f"Logged in as {user['name']} ({user['role']})")

            widget = MyWidget(user)
            widget.resize(1280, 720)
            widget.show()
            sys.exit(app.exec())
        else:
            print("Login cancelled.")
            sys.exit()
    except Exception as e:
        print(f"Crash occurred: {e}")
