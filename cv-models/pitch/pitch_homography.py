"""Pitch homography utilities.

Homography provides a projective transformation between image pixel
coordinates and real-world pitch coordinates. With at least four
non-collinear landmark correspondences, we can estimate a matrix H such
that: X_pitch ~ H * x_image.
"""

from typing import Dict, Tuple, Any, Optional

import cv2
import numpy as np


class PitchHomography:
    """Compute and apply a pitch homography matrix."""

    def __init__(self, pitch_points: Optional[Dict[str, Tuple[float, float]]] = None) -> None:
        """Initialize with optional canonical pitch point definitions.

        Args:
            pitch_points: Mapping of landmark names to canonical pitch coords.
        """
        self.pitch_points = pitch_points or {}
        self._H: Optional[np.ndarray] = None

    def compute_homography(self, keypoints: Dict[str, Tuple[float, float]]) -> Optional[np.ndarray]:
        """Estimate homography matrix from detected keypoints.

        Args:
            keypoints: Mapping of landmark names to pixel coordinates.

        Returns:
            3x3 homography matrix if successful, otherwise None.
        """
        src = []
        dst = []
        for name, pix in keypoints.items():
            if pix is None or name not in self.pitch_points:
                continue
            src.append(pix)
            dst.append(self.pitch_points[name])

        if len(src) < 4:
            self._H = None
            return None

        src_pts = np.array(src, dtype=np.float32)
        dst_pts = np.array(dst, dtype=np.float32)
        H, _ = cv2.findHomography(src_pts, dst_pts, method=cv2.RANSAC)
        self._H = H
        return H

    def map_to_pitch(self, pixel_point: Tuple[float, float]) -> Optional[Tuple[float, float]]:
        """Map a pixel coordinate to pitch coordinates using the homography.

        Args:
            pixel_point: (x, y) in image space.

        Returns:
            (x, y) in pitch coordinates, or None if homography is not set.
        """
        if self._H is None:
            return None

        pt = np.array([[pixel_point]], dtype=np.float32)
        mapped = cv2.perspectiveTransform(pt, self._H)[0][0]
        return float(mapped[0]), float(mapped[1])
