from ultralytics import YOLO


class VehicleDetector:
    def __init__(self):
        self.model = YOLO("yolo11n.pt")
        self.vehicle_classes = {"car", "motorcycle", "bus", "truck"}

    def detect_frame(self, frame):
        results = self.model(frame, verbose=False)[0]
        detections = []

        for box in results.boxes:
            class_id = int(box.cls[0])
            class_name = self.model.names[class_id]
            confidence = float(box.conf[0])

            if class_name in self.vehicle_classes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                detections.append({
                    "class_name": class_name,
                    "confidence": confidence,
                    "box": [x1, y1, x2, y2]
                })

        return detections