from PySide6 import QtWidgets, QtCore
from PySide6.QtGui import QImage, QPixmap
import cv2
import os
import threading
import time

class CameraThread(QtCore.QThread):
    frame_update = QtCore.Signal(object)
    alert_signal = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = False
        self.second_person_start_time = None

        # --- Load YOLOv3 Model (with dynamic paths) ---
        base_dir = os.path.dirname(os.path.abspath(__file__))
        yolo_folder = os.path.join(base_dir, "..", "assets", "yolo")

        cfg_path = os.path.join(yolo_folder, "yolov3.cfg")
        weights_path = os.path.join(yolo_folder, "yolov3.weights")
        names_path = os.path.join(yolo_folder, "coco.names")

        self.net = cv2.dnn.readNetFromDarknet(cfg_path, weights_path)
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

        with open(names_path, "r") as f:
            self.classes = [line.strip() for line in f.readlines()]

        self.output_layers = self.net.getUnconnectedOutLayersNames()

    def run(self):
        self.running = True
        cap = cv2.VideoCapture(0)

        while self.running:
            ret, frame = cap.read()
            if ret:
                person_count = self.detect_people(frame)

                # Update GUI frame
                self.frame_update.emit(frame)

                current_time = time.time()

                if person_count >= 2:
                    if self.second_person_start_time is None:
                        self.second_person_start_time = current_time
                    elif current_time - self.second_person_start_time >= 10:
                        self.alert_signal.emit("SECOND_PERSON_PRESENT")
                        self.second_person_start_time = None
                else:
                    self.second_person_start_time = None

            time.sleep(0.03)  # ~30 FPS

        cap.release()

    def stop(self):
        self.running = False
        self.wait()

    def detect_people(self, frame):
        height, width = frame.shape[:2]

        blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
        self.net.setInput(blob)
        outputs = self.net.forward(self.output_layers)

        person_count = 0

        for output in outputs:
            for detection in output:
                scores = detection[5:]
                class_id = int(scores.argmax())
                confidence = scores[class_id]

                if self.classes[class_id] == "person" and confidence > 0.5:
                    person_count += 1

        return person_count

class CameraWidget(QtWidgets.QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(640, 480)
        self.setStyleSheet("background-color: black;")
        self.camera_thread = CameraThread(self)
        self.camera_thread.frame_update.connect(self.update_frame)
        self.camera_thread.alert_signal.connect(self.show_alert)
        self.camera_thread.start()

    def update_frame(self, frame):
        image = QImage(
            frame.data, frame.shape[1], frame.shape[0], frame.strides[0],
            QImage.Format_BGR888
        )
        self.setPixmap(QPixmap.fromImage(image))

    def show_alert(self, message):
        if message == "SECOND_PERSON_PRESENT":
            self.parent().second_person_behind_detected = True
            print("⚡ Second person detected, flag set!")
        else:
            QtWidgets.QMessageBox.warning(self, "Alert", message)

    def closeEvent(self, event):
        self.camera_thread.stop()
        event.accept()
