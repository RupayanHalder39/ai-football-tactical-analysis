"""Ball detection module using YOLOv8.

Ball detection is challenging because the ball is small, often blurred,
frequently occluded, and can be confused with highlights or advertisements.
Small-object recall generally improves with higher-resolution inputs and
models trained specifically for ball instances.
"""

from typing import List, Dict, Any, Optional

from ultralytics import YOLO


class BallDetector:
    """YOLOv8-based ball detector.

    This detector filters for the "sports ball" class from the COCO label set.
    For football-specific use, the model should be fine-tuned on a dataset with
    ball annotations at broadcast resolution.
    """

    def __init__(self, model_path: Optional[str] = None) -> None:
        """Initialize the YOLOv8 model.

        Args:
            model_path: Optional path to a custom YOLOv8 model file.
                If not provided, a default pretrained model is used.
        """
        self.model = YOLO(model_path or "yolov8n.pt")

    def detect(self, frame) -> List[Dict[str, Any]]:
        """Detect footballs in a single frame.

        Args:
            frame: A video frame as a numpy array.

        Returns:
            List of detections in [x, y, w, h] format with confidence scores.
        """
        results = self.model.predict(frame, verbose=False)
        if not results:
            return []

        detections: List[Dict[str, Any]] = []
        boxes = results[0].boxes
        if boxes is None:
            return detections

        names = results[0].names
        for box in boxes:
            class_id = int(box.cls.item())
            class_name = names.get(class_id, "")
            if class_name != "sports ball":
                continue

            x1, y1, x2, y2 = box.xyxy[0].tolist()
            width = x2 - x1
            height = y2 - y1
            confidence = float(box.conf.item())

            detections.append(
                {
                    "bbox": [x1, y1, width, height],
                    "confidence": confidence,
                }
            )

        return detections
