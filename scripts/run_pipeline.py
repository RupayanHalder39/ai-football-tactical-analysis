"""Run a minimal end-to-end pipeline on a sample video.

This script is a lightweight harness for testing the pipeline shape. It:
- finds the first video in data/input
- processes frames with OpenCV (frame count + timestamps)
- generates dummy events and possession analytics
- writes results to results/sample_match_events.json

Usage:
    python scripts/run_pipeline.py
"""

from __future__ import annotations

from pathlib import Path
import json
from typing import List, Dict, Any, Tuple


def _project_root() -> Path:
    """Resolve the project root from the script location."""
    return Path(__file__).resolve().parents[1]


def _find_first_video(input_dir: Path) -> Path:
    """Find the first video in the input directory."""
    for ext in ("*.mp4", "*.mov", "*.mkv", "*.avi"):
        matches = sorted(input_dir.glob(ext))
        if matches:
            return matches[0]
    raise FileNotFoundError("No video found in data/input")


def _frame_to_timestamp(frame_index: int, fps: float) -> Tuple[float, str]:
    """Convert frame index to seconds and MM:SS clock."""
    if fps <= 0:
        return 0.0, "00:00"
    seconds = frame_index / fps
    minutes = int(seconds // 60)
    sec = int(seconds % 60)
    return seconds, f"{minutes:02d}:{sec:02d}"


def _generate_dummy_events(fps: float, total_frames: int) -> List[Dict[str, Any]]:
    """Generate a few placeholder events for testing output structure."""
    events = []
    for idx, event in enumerate(["pass", "dribble", "shot"], start=1):
        frame_idx = min(total_frames - 1, idx * int(fps * 5)) if total_frames > 0 else 0
        ts, clock = _frame_to_timestamp(frame_idx, fps)
        events.append({"timestamp": clock, "timestamp_seconds": ts, "event": event, "confidence": 0.8})
    return events


def _generate_possession(total_frames: int, fps: float) -> Tuple[Dict[str, float], List[Dict[str, Any]]]:
    """Generate dummy possession summary and timeline segments."""
    if total_frames <= 0:
        return {}, []

    mid_frame = total_frames // 2
    start_ts, start_clock = _frame_to_timestamp(0, fps)
    mid_ts, mid_clock = _frame_to_timestamp(mid_frame, fps)
    end_ts, end_clock = _frame_to_timestamp(total_frames - 1, fps)

    segments = [
        {"team": "Team_A", "start": start_clock, "end": mid_clock},
        {"team": "Team_B", "start": mid_clock, "end": end_clock},
    ]

    summary = {"Team_A": 50.0, "Team_B": 50.0}
    return summary, segments


def main() -> None:
    """Execute the minimal pipeline."""
    root = _project_root()
    input_dir = root / "data" / "input"
    results_dir = root / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    video_path = _find_first_video(input_dir)

    try:
        import cv2
    except Exception as exc:
        raise RuntimeError("OpenCV is required to run this script.") from exc

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError("Failed to open input video.")

    fps = cap.get(cv2.CAP_PROP_FPS) or 0.0
    total_frames = 0
    while cap.isOpened():
        ret, _frame = cap.read()
        if not ret:
            break
        total_frames += 1
    cap.release()

    events = _generate_dummy_events(fps, total_frames)
    possession_summary, possession_segments = _generate_possession(total_frames, fps)

    output = {
        "events": events,
        "possession_summary": possession_summary,
        "possession_segments": possession_segments,
    }

    out_path = results_dir / "sample_match_events.json"
    out_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"Wrote results to {out_path}")


if __name__ == "__main__":
    main()
