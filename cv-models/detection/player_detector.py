"""Player detection module (placeholder).

This module will eventually wrap a YOLOv8 (or similar) detector trained
for football player/goalkeeper detection. The interface is designed to
be model-agnostic so experiments can swap detectors without changing
pipeline code.
"""

from typing import List, Dict, Any


class PlayerDetector:
    """Placeholder player detector.

    In a future implementation, this class will:
    - Load a detection model (e.g., YOLOv8).
    - Perform inference on frames.
    - Return standardized bounding boxes and scores.
    """

    def __init__(self, config: Dict[str, Any] | None = None) -> None:
        """Initialize the detector with optional configuration."""
        self.config = config or {}

    def detect(self, frame) -> List[Dict[str, Any]]:
        """Detect players in a single frame (placeholder).

        Args:
            frame: A video frame as a numpy array.

        Returns:
            List of detection dicts with bounding boxes and confidence scores.
        """
        # TODO: Replace with real detector inference (e.g., YOLOv8 forward pass).
        return []
