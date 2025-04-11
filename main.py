import sys
from PySide6 import QtCore, QtWidgets, QtGui
from modules.systemalerts import get_battery_status
from modules.idle_tracker import get_idle_time
from modules.camera_feed import CameraWidget  # Import YOLO-powered camera widget
from modules.nasa_tlx import TLXForm  # ✅ NASA TLX form

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
        self.timer.start(1000)  # Update every second

        self.hide()  # Start hidden

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

        # self.camera_widget = CameraWidget(self)
        self.idle_timer_widget = IdleTimerWidget()
        self.battery_label = QtWidgets.QLabel("🔋 Battery: --%", alignment=QtCore.Qt.AlignRight)

        # Layout for battery at the bottom right
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.camera_widget)
        layout.addWidget(self.battery_label)
        layout.addWidget(self.notify_button)

        # Battery status tracking
        self.battery_timer = QtCore.QTimer(self)
        self.battery_timer.timeout.connect(self.update_battery_status)
        self.battery_timer.start(3000)

        self.was_plugged_in = True

        # ✅ Auto NASA TLX popup every hour
        self.tlx_timer = QtCore.QTimer(self)
        self.tlx_timer.timeout.connect(self.prompt_tlx)
        self.tlx_timer.start(60 * 60 * 1000)

    @QtCore.Slot()
    def update_battery_status(self):
        percentage, is_plugged_in = get_battery_status()
        self.battery_label.setText(f"🔋 Battery: {percentage}%")

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    widget = MyWidget()
    widget.resize(1280, 720)
    widget.show()
    sys.exit(app.exec())
