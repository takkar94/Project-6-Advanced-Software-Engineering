import cv2
import numpy as np
from PySide6 import QtCore, QtWidgets, QtGui

class CameraThread(QtCore.QThread):
    """ Separate thread for capturing frames from OpenCV to avoid GUI lag. """
    frame_signal = QtCore.Signal(QtGui.QImage)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cap = cv2.VideoCapture(0)  # Open the camera
        self.running = True  # Control flag

    def run(self):
        """ Capture frames and emit as Qt-compatible images. """
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert to RGB
                height, width, channels = frame.shape
                bytes_per_line = channels * width
                q_image = QtGui.QImage(frame.data, width, height, bytes_per_line, QtGui.QImage.Format_RGB888)
                self.frame_signal.emit(q_image)  # Send frame to UI
            self.msleep(30)  # Limit FPS (~30fps)

    def stop(self):
        """ Stop the camera thread safely. """
        self.running = False
        self.quit()
        self.wait()
        self.cap.release()

class CameraWidget(QtWidgets.QWidget):
    """ Widget to display the camera feed in a QLabel. """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Video display
        self.video_label = QtWidgets.QLabel(self)
        self.video_label.setFixedSize(640, 480)  # Set a fixed size

        # Layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.video_label)

        # Start camera thread
        self.camera_thread = CameraThread()
        self.camera_thread.frame_signal.connect(self.update_frame)
        self.camera_thread.start()

    def update_frame(self, image):
        """ Update QLabel with the latest camera frame. """
        self.video_label.setPixmap(QtGui.QPixmap.fromImage(image))

    def closeEvent(self, event):
        """ Ensure the camera thread is stopped when closing. """
        self.camera_thread.stop()
        event.accept()
