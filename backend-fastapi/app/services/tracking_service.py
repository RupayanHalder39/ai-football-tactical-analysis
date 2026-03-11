"""Tracking service stubs.

This module contains placeholder tracking logic. It will be replaced
by a real tracker (e.g., ByteTrack/DeepSORT) later in the project.
"""


def track_objects(detections):
    """Assign simple incremental IDs to detected players (placeholder).

    Args:
        detections: Detection output with players and ball.

    Returns:
        List of tracked player objects with IDs attached.
    """
    tracked = []
    for idx, player in enumerate(detections.get("players", []), start=1):
        tracked.append(
            {
                "player_id": idx,
                "bbox": player["bbox"],
            }
        )
    return tracked
