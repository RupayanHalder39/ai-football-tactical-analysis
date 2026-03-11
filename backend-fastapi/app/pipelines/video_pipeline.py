"""Video analysis pipeline orchestrating core CV services.

This module provides the first working milestone pipeline:
- Read video from disk.
- Extract frames.
- Run placeholder detection and tracking.
- Return structured JSON for the first 10 frames.
"""

from app.schemas.response_schema import FrameResult, VideoAnalysisResponse
from app.services.detection_service import detect_objects
from app.services.tracking_service import track_objects
from app.utils.video_utils import extract_frames


def process_video(video_path: str) -> VideoAnalysisResponse:
    """Process a video file and return placeholder tracking results.

    Args:
        video_path: Path to the saved video file.

    Returns:
        VideoAnalysisResponse containing per-frame placeholder results.
    """
    # 1) Extract frames from the input video.
    frames = extract_frames(video_path)

    # 2) Process only the first 10 frames for now to keep it fast.
    results = []
    for idx, frame in enumerate(frames[:10], start=1):
        # 3) Placeholder detection stage.
        detections = detect_objects(frame)

        # 4) Placeholder tracking stage.
        tracked_players = track_objects(detections)

        # 5) Build response schema for this frame.
        results.append(
            FrameResult(
                frame_id=idx,
                players=tracked_players,
                ball=detections.get("ball", {}),
            )
        )

    return VideoAnalysisResponse(frames=results)
