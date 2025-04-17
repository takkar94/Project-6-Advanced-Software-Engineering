from PySide6 import QtWidgets, QtCore

class FrustrationDistractionDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🧘 Frustration Distraction")
        self.setFixedSize(400, 250)

        # Main layout
        layout = QtWidgets.QVBoxLayout(self)

        # Inspirational message
        self.quote_label = QtWidgets.QLabel("“Breathe. You're doing just fine.”")
        self.quote_label.setAlignment(QtCore.Qt.AlignCenter)
        self.quote_label.setStyleSheet("""
            font-size: 16px;
            font-style: italic;
            color: #444;
        """)

        # Countdown before activation
        self.timer_label = QtWidgets.QLabel("Ready in 5 seconds...")
        self.timer_label.setAlignment(QtCore.Qt.AlignCenter)
        self.timer_label.setStyleSheet("font-size: 14px; color: #666;")

        # Completion button
        self.done_button = QtWidgets.QPushButton("✅ I'm ready to refocus")
        self.done_button.setEnabled(False)
        self.done_button.clicked.connect(self.accept)

        layout.addStretch()
        layout.addWidget(self.quote_label)
        layout.addWidget(self.timer_label)
        layout.addWidget(self.done_button)
        layout.addStretch()

        self.seconds_left = 5
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)

    def update_timer(self):
        self.seconds_left -= 1
        if self.seconds_left <= 0:
            self.timer.stop()
            self.timer_label.setText("You're good to go!")
            self.done_button.setEnabled(True)
        else:
            self.timer_label.setText(f"Ready in {self.seconds_left} seconds...")
