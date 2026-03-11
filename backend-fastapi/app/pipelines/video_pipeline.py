"""Video analysis pipeline orchestrating the CV library and event engine.

This module runs the full CV stack on an uploaded video and returns a
job-result payload containing:
- per-frame player/ball data
- events timeline
- possession summary and segments

No hardcoded analytics are returned; all outputs are computed dynamically.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional
import importlib
import importlib.util
import sys


_cv_modules: Dict[str, Any] = {}


def _project_root() -> Path:
    """Resolve the monorepo project root from this file location."""
    return Path(__file__).resolve().parents[3]


def _load_cv_package() -> None:
    """Load cv-models as an importable package without hardcoded paths."""
    if _cv_modules.get("loaded"):
        return

    project_root = _project_root()
    cv_root = project_root / "cv-models"
    pkg_name = "cv_models"
    init_path = cv_root / "__init__.py"

    spec = importlib.util.spec_from_file_location(pkg_name, init_path, submodule_search_locations=[str(cv_root)])
    module = importlib.util.module_from_spec(spec)
    sys.modules[pkg_name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)

    _cv_modules["video_processor"] = importlib.import_module(f"{pkg_name}.video_processor")
    _cv_modules["event_engine"] = importlib.import_module(f"{pkg_name}.event_engine")
    _cv_modules["loaded"] = True


def _attach_player_metrics(frames: List[Dict[str, Any]]) -> None:
    """Attach speed and distance metrics to each player if available."""
    for frame in frames:
        analytics = frame.get("analytics") or {}
        speeds = analytics.get("player_speed") or {}
        distances = analytics.get("distance_covered") or {}
        team_labels = frame.get("teams") or []
        team_map = {t.get("track_id"): t.get("team") for t in team_labels if isinstance(t, dict)}

        for player in frame.get("players", []) or []:
            track_id = player.get("track_id")
            if track_id is None:
                continue
            speed = speeds.get(track_id, speeds.get(str(track_id)))
            distance = distances.get(track_id, distances.get(str(track_id)))
            player["speed"] = speed
            player["distance"] = distance
            if player.get("team") is None and track_id in team_map:
                player["team"] = team_map.get(track_id)


def _enrich_events(events: List[Dict[str, Any]], frames: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Enrich events with x/y coordinates from closest frame."""
    if not events or not frames:
        return events

    def closest_frame(ts: Optional[float]) -> Optional[Dict[str, Any]]:
        if ts is None:
            return None
        best = None
        best_diff = None
        for frame in frames:
            fts = frame.get("timestamp_seconds")
            if fts is None:
                continue
            diff = abs(fts - ts)
            if best_diff is None or diff < best_diff:
                best_diff = diff
                best = frame
        return best

    for event in events:
        ts = event.get("timestamp_seconds")
        frame = closest_frame(ts)
        if not frame:
            event.setdefault("x", None)
            event.setdefault("y", None)
            event.setdefault("outcome", None)
            continue

        ball = frame.get("ball") or {}
        x = ball.get("pitch_x") or ball.get("x")
        y = ball.get("pitch_y") or ball.get("y")
        event.setdefault("x", x)
        event.setdefault("y", y)
        event.setdefault("outcome", None)

    return events


def process_video(video_path: str, match_id: Optional[str] = None) -> Dict[str, Any]:
    """Run the CV pipeline and EventEngine for a single video.

    Args:
        video_path: Path to uploaded video.
        match_id: Optional match/job identifier.

    Returns:
        Job-result dictionary with frames, events, possession summary, and segments.
    """
    _load_cv_package()

    VideoProcessor = _cv_modules["video_processor"].VideoProcessor
    EventEngine = _cv_modules["event_engine"].EventEngine

    processor = VideoProcessor(frame_skip=0)
    metadata = {
        "match_id": match_id or Path(video_path).stem,
        "video_source": video_path,
    }
    dataset = processor.process_video(video_path, match_metadata=metadata)
    frames = dataset.get("frames", [])

    _attach_player_metrics(frames)

    engine = EventEngine(window_size=20)
    event_output = engine.detect(frames)

    events = _enrich_events(event_output.get("events", []), frames)

    return {
        "match_metadata": dataset.get("match_metadata", metadata),
        "events": events,
        "possession_summary": event_output.get("possession_summary", {}),
        "possession_segments": event_output.get("possession_segments", []),
        "frames": frames,
    }
