"""Player detection module using YOLOv8.

This module wraps a YOLOv8 model from the Ultralytics library to detect
players in a single frame. For now, detections are filtered to the
\"person\" class. Later, this detector can be fine-tuned on football
datasets to better separate players, goalkeepers, referees, and staff.
"""

from typing import List, Dict, Any, Optional

from ultralytics import YOLO


class PlayerDetector:
    """YOLOv8-based player detector.

    The detector runs inference on a frame and returns bounding boxes in
    [x, y, width, height] format with confidence scores. Only \"person\"
    class detections are included.
    """

    def __init__(self, model_path: Optional[str] = None) -> None:
        """Initialize the YOLOv8 model.

        Args:
            model_path: Optional path to a custom YOLOv8 model file.
                If not provided, a default pretrained model is used.
        """
        # Default to a lightweight pretrained model for fast prototyping.
        self.model = YOLO(model_path or "yolov8n.pt")

    def detect(self, frame) -> List[Dict[str, Any]]:
        """Detect players in a single frame using YOLOv8.

        YOLO returns bounding boxes in xyxy format. We convert them to
        [x, y, width, height] for downstream consistency.

        Args:
            frame: A video frame as a numpy array (BGR or RGB is supported by YOLO).

        Returns:
            List of detection dicts with bounding boxes and confidence scores.
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
            if class_name != "person":
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
