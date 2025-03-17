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

        # Load YOLO model from assets/yolo/
        self.net = cv2.dnn.readNet("assets/yolo/yolov3.weights", "assets/yolo/yolov3.cfg")
        self.classes = open("assets/yolo/coco.names").read().strip().split("\n")
        self.layer_names = self.net.getLayerNames()
        self.output_layers = [self.layer_names[i - 1] for i in self.net.getUnconnectedOutLayers()]

        self.frame_count = 0  # Track frames for YOLO processing
        self.last_detections = []  # Cache last detections

    def run(self):
        """ Capture frames, detect objects (every N frames), and emit processed images. """
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                continue

            height, width = frame.shape[:2]

            # Process YOLO every 5th frame to reduce lag
            if self.frame_count % 5 == 0:
                resized_frame = cv2.resize(frame, (320, 320))  # Downscale for faster YOLO processing
                blob = cv2.dnn.blobFromImage(resized_frame, scalefactor=1/255.0, size=(416, 416), swapRB=True, crop=False)
                self.net.setInput(blob)
                detections = self.net.forward(self.output_layers)

                boxes, confidences = [], []
                for output in detections:
                    for detection in output:
                        scores = detection[5:]
                        class_id = np.argmax(scores)
                        confidence = scores[class_id]

                        if confidence > 0.5 and self.classes[class_id] == "person":
                            x, y, w, h = (detection[:4] * np.array([width, height, width, height])).astype("int")
                            x1, y1 = int(x - w / 2), int(y - h / 2)
                            x2, y2 = int(x1 + w), int(y1 + h)

                            boxes.append([x1, y1, w, h])
                            confidences.append(float(confidence))

                # Apply Non-Maximum Suppression (NMS) safely
                indices = cv2.dnn.NMSBoxes(boxes, confidences, score_threshold=0.5, nms_threshold=0.4)
                if isinstance(indices, tuple) or len(indices) == 0:  
                    self.last_detections = []  # No detections found
                else:
                    self.last_detections = [boxes[i] for i in indices.flatten()]  # Fix indexing

            self.frame_count += 1

            # Draw bounding boxes from the last processed frame
            for (x1, y1, w, h) in self.last_detections:
                x2, y2 = x1 + w, y1 + h
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, "Person", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert to RGB
            q_image = QtGui.QImage(frame.data, width, height, frame.strides[0], QtGui.QImage.Format_RGB888)
            self.frame_signal.emit(q_image)  # Send processed frame to UI
            self.msleep(30)  # Reduce delay for smoother FPS

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
