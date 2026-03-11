"""Player tracking module using ByteTrack.

This module assigns persistent IDs to player detections across frames.
ByteTrack associates detections frame-to-frame by combining high- and
low-confidence boxes, improving ID continuity under occlusion.

Notes:
- This class expects detections from PlayerDetector in [x, y, w, h] format.
- The implementation is independent of FastAPI and can be reused in any
  research pipeline.
"""

from __future__ import annotations

from typing import Dict, List, Any, Optional

import numpy as np


class PlayerTracker:
    """ByteTrack-based multi-object tracker for players.

    ByteTrack maintains trajectories by linking detections across frames
    using motion and appearance-agnostic association. It keeps IDs stable
    when players are briefly lost and reappear.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the ByteTrack tracker with reasonable defaults.

        Args:
            config: Optional configuration dict for tuning tracker behavior.
        """
        self.config = config or {}

        # Import lazily to keep the module lightweight if tracking isn't used.
        try:
            import supervision as sv
        except Exception as exc:  # pragma: no cover - import guard
            raise ImportError(
                "ByteTrack requires the 'supervision' package. "
                "Install it with: pip install supervision"
            ) from exc

        # Basic defaults that work for many videos; can be overridden via config.
        self.tracker = sv.ByteTrack(
            track_thresh=self.config.get("track_thresh", 0.25),
            match_thresh=self.config.get("match_thresh", 0.8),
            track_buffer=self.config.get("track_buffer", 30),
            frame_rate=self.config.get("frame_rate", 30),
        )
        self._sv = sv

    def update(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Update tracker state with detections from the current frame.

        Args:
            detections: List of dicts with keys:
                - bbox: [x, y, w, h]
                - confidence: float

        Returns:
            List of tracked detections with persistent IDs:
                - track_id: int
                - bbox: [x, y, w, h]
                - confidence: float
        """
        if not detections:
            return []

        # Convert [x, y, w, h] to xyxy for ByteTrack.
        xyxy = []
        confidences = []
        class_ids = []
        for det in detections:
            x, y, w, h = det["bbox"]
            xyxy.append([x, y, x + w, y + h])
            confidences.append(det.get("confidence", 0.0))
            class_ids.append(0)  # single-class (person) tracking

        sv_dets = self._sv.Detections(
            xyxy=np.array(xyxy, dtype=np.float32),
            confidence=np.array(confidences, dtype=np.float32),
            class_id=np.array(class_ids, dtype=np.int32),
        )

        tracked = self.tracker.update_with_detections(sv_dets)

        # Map tracked detections back to [x, y, w, h] with track IDs.
        results: List[Dict[str, Any]] = []
        for det in tracked:
            # supervision returns: [xyxy, confidence, class_id, tracker_id]
            x1, y1, x2, y2 = det[0].tolist()
            conf = float(det[2]) if len(det) > 2 else 0.0
            track_id = int(det[4]) if len(det) > 4 else -1
            results.append(
                {
                    "track_id": track_id,
                    "bbox": [x1, y1, x2 - x1, y2 - y1],
                    "confidence": conf,
                }
            )

        return results
