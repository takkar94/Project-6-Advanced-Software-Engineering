import sys
from PySide6 import QtCore, QtWidgets, QtGui
from modules.systemalerts import get_battery_status
from modules.idle_tracker import get_idle_time
from modules.camera_feed import CameraWidget  # Import camera widget

# --- Idle Timer Widget ---
class IdleTimerWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setFixedSize(250, 80)  # Increased size

        # Label to display idle time
        self.timer_label = QtWidgets.QLabel("Idle Time: 0s", self)
        self.timer_label.setAlignment(QtCore.Qt.AlignCenter)
        self.timer_label.setStyleSheet("""
            background: black; 
            color: white; 
            font-size: 18px; 
            font-weight: bold;
            padding: 15px; 
            border-radius: 15px;
        """)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.timer_label)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_idle_timer)
        self.timer.start(1000)  # Update every second

        self.show_timer()

    def update_idle_timer(self):
        """Update the displayed idle time every second."""
        idle_time = int(get_idle_time())
        self.timer_label.setText(f"Idle Time: {idle_time}s")

        # Change color if idle time exceeds 30 seconds
        if idle_time > 30:
            self.timer_label.setStyleSheet("""
                background: red; 
                color: white; 
                font-size: 18px; 
                font-weight: bold;
                padding: 15px; 
                border-radius: 15px;
            """)
        else:
            self.timer_label.setStyleSheet("""
                background: black; 
                color: white; 
                font-size: 18px; 
                font-weight: bold;
                padding: 15px; 
                border-radius: 15px;
            """)

    def show_timer(self):
        """Position the timer at the bottom-right corner of the screen."""
        screen_geometry = QtWidgets.QApplication.primaryScreen().availableGeometry()
        self.move(screen_geometry.width() - 270, screen_geometry.height() - 100)  # Adjusted position
        self.show()

# --- Main Application Widget ---
class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # --- System Tray Icon ---
        self.tray_icon = QtWidgets.QSystemTrayIcon(QtGui.QIcon("assets/warning.png"), self)
        self.tray_icon.setVisible(True)

        # --- Battery Status Label ---
        self.battery_label = QtWidgets.QLabel("🔋 Battery: --%", alignment=QtCore.Qt.AlignRight)

        # --- Camera Widget ---
        self.camera_widget = CameraWidget(self)

        # --- Idle Timer Widget ---
        self.idle_timer_widget = IdleTimerWidget()

        # --- Layouts ---
        main_layout = QtWidgets.QHBoxLayout(self)

        left_layout = QtWidgets.QVBoxLayout()
        left_layout.addWidget(self.camera_widget)

        right_layout = QtWidgets.QVBoxLayout()
        right_layout.addWidget(self.battery_label)

        main_layout.addLayout(left_layout, 1)  # Left side (50%)
        main_layout.addLayout(right_layout, 1)  # Right side (50%)

        # --- Timers ---
        self.battery_timer = QtCore.QTimer(self)
        self.battery_timer.timeout.connect(self.update_battery_status)
        self.battery_timer.start(3000)  # Refresh every 3 seconds

        self.update_battery_status()

    @QtCore.Slot()
    def update_battery_status(self):
        status_message, notification_stat = get_battery_status()
        percentage = status_message.split(":")[1].split("%")[0].strip()
        self.battery_label.setText(f"🔋 Battery: {percentage}%")

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MyWidget()
    widget.resize(1280, 720)
    widget.show()

    sys.exit(app.exec())
