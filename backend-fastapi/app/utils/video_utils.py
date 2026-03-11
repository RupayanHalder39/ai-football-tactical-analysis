"""Video utilities for frame extraction."""

from typing import List

import cv2


def extract_frames(video_path: str) -> List:
    """Extract frames from a video file using OpenCV.

    Args:
        video_path: Path to the video file on disk.

    Returns:
        A list of frames as numpy arrays.

    Raises:
        ValueError: If the video cannot be opened or frames cannot be read.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("Failed to open video file.")

    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)

    cap.release()

    if not frames:
        raise ValueError("No frames extracted from video.")

    return frames
