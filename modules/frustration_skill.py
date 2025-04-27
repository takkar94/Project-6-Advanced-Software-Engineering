from PySide6 import QtWidgets, QtCore, QtGui

class BreathingCircle(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 200)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.radius = 50
        self.growing = True

        # Create a timer inside the circle itself
        self.animation_timer = QtCore.QTimer(self)
        self.animation_timer.timeout.connect(self.animate)
        self.animation_timer.start(50)  # 20 frames per second

    def animate(self):
        if self.growing:
            self.radius += 1
            if self.radius >= 100:
                self.growing = False
        else:
            self.radius -= 1
            if self.radius <= 50:
                self.growing = True
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        rect = self.rect()
        center = rect.center()

        # Fill background
        painter.fillRect(rect, QtGui.QColor("#ffffff"))

        # Draw circle
        pen = QtGui.QPen(QtGui.QColor("#5dade2"))
        pen.setWidth(5)
        painter.setPen(pen)
        painter.setBrush(QtGui.QBrush(QtGui.QColor("#aed6f1")))
        painter.drawEllipse(center, self.radius, self.radius)

class FrustrationDistractionDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Breathe and Refocus 🌿")
        self.setMinimumSize(400, 500)

        layout = QtWidgets.QVBoxLayout(self)

        self.label = QtWidgets.QLabel(
            "Let's take a few deep breaths...\n\n"
            "Follow the expanding and contracting circle."
        )
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setStyleSheet("font-size: 16px;")

        self.breathing_circle = BreathingCircle()

        self.refocus_button = QtWidgets.QPushButton("✅ I'm Ready to Refocus")
        self.refocus_button.setEnabled(False)
        self.refocus_button.clicked.connect(self.accept)

        layout.addWidget(self.label)
        layout.addStretch()
        layout.addWidget(self.breathing_circle, alignment=QtCore.Qt.AlignCenter)
        layout.addStretch()
        layout.addWidget(self.refocus_button)

        # Unlock refocus button after 30 seconds
        self.unlock_timer = QtCore.QTimer(self)
        self.unlock_timer.setSingleShot(True)
        self.unlock_timer.timeout.connect(self.enable_refocus_button)
        self.unlock_timer.start(30000)

    def enable_refocus_button(self):
        self.refocus_button.setEnabled(True)
        self.label.setText(
            "Well done! You're ready to continue. 🌟\n\nClick the button below."
        )
