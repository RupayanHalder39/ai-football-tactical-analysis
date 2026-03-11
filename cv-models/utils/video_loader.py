"""Video loading utilities.

This module provides a minimal frame loader that can be reused across
research experiments without tying to any specific pipeline.
"""

from typing import List

import cv2


def load_video_frames(video_path: str) -> List:
    """Load all frames from a video file.

    Args:
        video_path: Path to the video file.

    Returns:
        List of frames as numpy arrays.

    Raises:
        ValueError: If the video cannot be opened or has no frames.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("Unable to open video file.")

    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)

    cap.release()

    if not frames:
        raise ValueError("No frames loaded from video.")

    return frames
