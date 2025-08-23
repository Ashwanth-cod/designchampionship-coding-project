import cv2
from ultralytics import YOLO

class WebcamClassifier:
    def __init__(self, model_path: str):
        try:
            self.model = YOLO(model_path)
        except Exception as e:
            print(f"[ERROR] Could not load YOLO model: {e}")
            self.model = None

    def capture_and_classify(self):
        if self.model is None:
            return "not_found", "YOLO model not loaded."

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return "not_found", "Could not access webcam."

        ret, frame = cap.read()
        cap.release()
        if not ret:
            return "not_found", "Failed to capture image."

        results = self.model.predict(frame)
        if len(results) == 0 or len(results[0].boxes) == 0:
            return "not_found", "No object detected."

        cls_id = int(results[0].boxes[0].cls)
        names = self.model.names
        return names.get(cls_id, "not_found"), "Prediction complete."
