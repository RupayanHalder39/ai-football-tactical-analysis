"""Detection service stubs.

This module contains placeholder detection logic. It will be replaced
by a real detector (e.g., YOLO) later in the project.
"""


def detect_objects(frame):
    """Detect players and ball in a single frame (placeholder).

    Args:
        frame: A single video frame as a numpy array.

    Returns:
        A mock detection structure with players and ball data.
    """
    # TODO: Replace this with real detection outputs from a model.
    return {
        "players": [
            {
                "bbox": [100, 200, 50, 80],
                "confidence": 0.9,
            }
        ],
        "ball": {
            "bbox": [300, 400, 20, 20],
        },
    }
