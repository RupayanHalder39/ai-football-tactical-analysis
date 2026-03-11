"""Pitch coordinate mapping utilities.

This module provides a lightweight homography-based mapper that converts
pixel coordinates from broadcast frames into real-world pitch coordinates
(in meters). Having both coordinate spaces enables spatial analytics such
as progressive passes, penalty-box entries, and tactical shape analysis.
"""

from __future__ import annotations

from typing import List, Dict, Any, Tuple, Optional

import cv2
import numpy as np


PITCH_LENGTH_M = 105.0
PITCH_WIDTH_M = 68.0


def compute_homography(image_points: List[Tuple[float, float]], pitch_points: List[Tuple[float, float]]) -> Optional[np.ndarray]:
    """Compute a homography matrix from image points to pitch points.

    Args:
        image_points: List of (x, y) pixel coordinates from the frame.
        pitch_points: List of (x, y) pitch coordinates in meters.

    Returns:
        3x3 homography matrix or None if estimation fails.
    """
    if len(image_points) < 4 or len(pitch_points) < 4:
        return None

    src = np.array(image_points, dtype=np.float32)
    dst = np.array(pitch_points, dtype=np.float32)
    H, _ = cv2.findHomography(src, dst, method=cv2.RANSAC)
    return H


class PitchMapper:
    """Map pixel coordinates to pitch coordinates using homography.

    The mapper preserves original pixel coordinates and adds pitch_x/pitch_y
    fields in meters. This separation allows analytics to use whichever
    coordinate space is appropriate.
    """

    def __init__(self, homography_matrix: Optional[np.ndarray]) -> None:
        """Initialize with a homography matrix.

        Args:
            homography_matrix: 3x3 matrix mapping pixels to pitch coords.
        """
        self.homography_matrix = homography_matrix

    def pixel_to_pitch(self, x: float, y: float) -> Optional[Tuple[float, float]]:
        """Transform a pixel coordinate into pitch coordinates.

        Args:
            x: Pixel x-coordinate.
            y: Pixel y-coordinate.

        Returns:
            (pitch_x, pitch_y) in meters or None if homography is missing.
        """
        if self.homography_matrix is None:
            return None

        pt = np.array([[[x, y]]], dtype=np.float32)
        mapped = cv2.perspectiveTransform(pt, self.homography_matrix)[0][0]
        return float(mapped[0]), float(mapped[1])

    def transform_players(self, players: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add pitch coordinates to each player record.

        Args:
            players: List of player dicts with bbox in [x, y, w, h].

        Returns:
            Updated list with x, y, pitch_x, pitch_y fields.
        """
        for player in players:
            bbox = player.get("bbox")
            if not bbox:
                continue
            x, y, w, h = bbox
            px = x + w / 2.0
            py = y + h
            player["x"] = px
            player["y"] = py
            pitch = self.pixel_to_pitch(px, py)
            if pitch is None:
                player["pitch_x"] = None
                player["pitch_y"] = None
            else:
                player["pitch_x"], player["pitch_y"] = pitch
        return players

    def transform_ball(self, ball: Dict[str, Any]) -> Dict[str, Any]:
        """Add pitch coordinates to the ball record.

        Args:
            ball: Ball dict with bbox in [x, y, w, h].

        Returns:
            Updated ball dict with x, y, pitch_x, pitch_y fields.
        """
        bbox = ball.get("bbox") if isinstance(ball, dict) else None
        if not bbox:
            return ball

        x, y, w, h = bbox
        px = x + w / 2.0
        py = y + h / 2.0
        ball["x"] = px
        ball["y"] = py
        pitch = self.pixel_to_pitch(px, py)
        if pitch is None:
            ball["pitch_x"] = None
            ball["pitch_y"] = None
        else:
            ball["pitch_x"], ball["pitch_y"] = pitch
        return ball
