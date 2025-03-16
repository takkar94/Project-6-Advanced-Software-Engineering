import sys
from PySide6 import QtCore, QtWidgets, QtGui
from modules.systemalerts import get_battery_status
from modules.idle_tracker import get_idle_time
from modules.camera_feed import CameraWidget  # Import camera widget

class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # --- Track Previous Power & Idle Status ---
        self.previous_status = None  # Stores last known power state
        self.previous_idle_state = False  # Track if user was idle

        # --- System Tray Icon ---
        self.tray_icon = QtWidgets.QSystemTrayIcon(QtGui.QIcon("assets/warning.png"), self)
        self.tray_icon.setVisible(True)

        # --- Battery Status Label ---
        self.battery_label = QtWidgets.QLabel("🔋 Battery: --%", alignment=QtCore.Qt.AlignRight)

        # --- Camera Widget (Left Side) ---
        self.camera_widget = CameraWidget(self)

        # --- Layouts ---
        main_layout = QtWidgets.QHBoxLayout(self)

        # Left side: Camera feed (50%)
        left_layout = QtWidgets.QVBoxLayout()
        left_layout.addWidget(self.camera_widget)

        # Right side: Battery Info
        right_layout = QtWidgets.QVBoxLayout()
        right_layout.addWidget(self.battery_label)

        # Add layouts to main layout
        main_layout.addLayout(left_layout, 1)  # Left side (50%)
        main_layout.addLayout(right_layout, 1)  # Right side (50%)

        # --- Timers ---
        self.battery_timer = QtCore.QTimer(self)
        self.battery_timer.timeout.connect(self.update_battery_status)
        self.battery_timer.start(3000)  # Refresh every 3 seconds

        self.idle_timer = QtCore.QTimer(self)
        self.idle_timer.timeout.connect(self.check_idle_time)
        self.idle_timer.start(5000)  # Check idle time every 5 seconds

        # --- Initial Updates ---
        self.update_battery_status()
        self.check_idle_time()

    @QtCore.Slot()
    def update_battery_status(self):
        status_message, notification_stat = get_battery_status()

        # Extract battery percentage
        percentage = status_message.split(":")[1].split("%")[0].strip()
        self.battery_label.setText(f"🔋 Battery: {percentage}%")

        # Notify only when power gets disconnected
        if self.previous_status is not None and self.previous_status == 1 and notification_stat == 0:
            self.show_system_tray_notification("Power Alert", "⚠️ Power Source Disconnected!")

        # Update previous power status
        self.previous_status = notification_stat

    @QtCore.Slot()
    def check_idle_time(self):
        idle_time = get_idle_time()

        if idle_time > 30 and not self.previous_idle_state:
            self.show_system_tray_notification("Idle Alert", "⏳ You've been inactive for 30+ seconds!")
            self.previous_idle_state = True  # Avoid repeated notifications

        elif idle_time < 5:
            self.previous_idle_state = False  # Reset when active

    def show_system_tray_notification(self, title, message):
        """ Show Windows-style notification in the system tray. """
        self.tray_icon.showMessage(title, message, QtWidgets.QSystemTrayIcon.Warning)

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MyWidget()
    widget.resize(1280, 720)  # Adjusted for better UI balance
    widget.show()

    sys.exit(app.exec())
