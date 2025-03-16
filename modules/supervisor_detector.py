import cv2
import numpy as np

# Load YOLO model
yolo_net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
layer_names = yolo_net.getLayerNames()
output_layers = [layer_names[i - 1] for i in yolo_net.getUnconnectedOutLayers()]

# Load COCO labels (80 classes)
with open("coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]

# Initialize the video capture
cap = cv2.VideoCapture(0)  # Open the default camera

def detect_people(frame):
    height, width, _ = frame.shape

    # Convert image to YOLO format
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), swapRB=True, crop=False)
    yolo_net.setInput(blob)
    detections = yolo_net.forward(output_layers)

    people_detected = []
    
    for output in detections:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            # Only detect people (Class ID for 'person' in COCO is 0)
            if classes[class_id] == "person" and confidence > 0.5:
                center_x, center_y, w, h = (detection[:4] * np.array([width, height, width, height])).astype("int")
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                # Store person location
                people_detected.append((x, y, w, h, confidence))

    return people_detected

def is_person_behind(frame, people_detected):
    """ Check if a person is detected behind the user (e.g., top-middle of frame) """
    frame_height, frame_width, _ = frame.shape
    center_x_range = (frame_width // 3, 2 * frame_width // 3)  # Middle third of frame (approx. behind user)
    upper_half = frame_height // 2  # Focus on upper part of the frame

    for (x, y, w, h, conf) in people_detected:
        person_center_x = x + w // 2
        person_center_y = y + h // 2

        if center_x_range[0] <= person_center_x <= center_x_range[1] and person_center_y < upper_half:
            return True  # Person is in the designated "behind" area

    return False

