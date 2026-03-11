"""Event detection engine operating on frame-level analytics datasets.

This module intentionally operates on a saved JSONL dataset instead of
running inside the per-frame CV pipeline. This design provides temporal
context, which is essential for detecting football events such as passes,
shots, and counter-attacks.

JSONL format expected:
- Line 1: {"match_metadata": {...}}
- Remaining lines: frame analytics dicts with timestamps and tracked data
"""

from __future__ import annotations

from typing import Dict, Any, List, Optional, Tuple
import json
from pathlib import Path


class EventEngine:
    """Detect football events from a frame analytics dataset.

    The engine uses heuristic rules over sliding windows of frames to capture
    temporal context. This makes event detection more robust than per-frame
    logic and keeps the design modular so ML models can replace heuristics later.
    """

    def __init__(self, window_size: int = 20, possession_distance: float = 5.0) -> None:
        """Initialize the event engine.

        Args:
            window_size: Number of frames to consider for temporal heuristics.
            possession_distance: Distance threshold for ball possession (pitch units).
        """
        self.window_size = max(1, window_size)
        self.possession_distance = possession_distance

    def load_dataset(self, jsonl_path: str) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """Load match metadata and frames from JSONL.

        Args:
            jsonl_path: Path to the JSONL dataset produced by VideoProcessor.

        Returns:
            (match_metadata, frames)
        """
        path = Path(jsonl_path)
        if not path.exists():
            raise FileNotFoundError(f"Dataset not found: {jsonl_path}")

        match_metadata: Dict[str, Any] = {}
        frames: List[Dict[str, Any]] = []

        with path.open("r", encoding="utf-8") as f:
            for idx, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                record = json.loads(line)
                if idx == 0 and "match_metadata" in record:
                    match_metadata = record["match_metadata"]
                else:
                    frames.append(record)

        return match_metadata, frames

    def detect(self, frames: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect events and compute possession summaries from frames.

        Returns a dict containing:
        - events: list of detected events
        - possession_summary: percentage possession by team
        - possession_segments: contiguous possession periods
        """
        events = self.detect_events(frames)
        possession_summary, possession_segments = self.compute_possession(frames)
        return {
            "events": events,
            "possession_summary": possession_summary,
            "possession_segments": possession_segments,
        }

    def detect_events(self, frames: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect events from frame sequences using sliding windows.

        Args:
            frames: List of frame analytics dicts.

        Returns:
            List of event dicts with timestamps and labels.
        """
        events: List[Dict[str, Any]] = []
        if not frames:
            return events

        for i in range(len(frames)):
            window = frames[max(0, i - self.window_size + 1) : i + 1]
            current = frames[i]

            shot_event = self._detect_shot(window)
            if shot_event:
                events.append(self._build_event(current, "shot", shot_event))

            pass_event = self._detect_pass(window)
            if pass_event:
                events.append(self._build_event(current, "pass", pass_event))

            dribble_event = self._detect_dribble(window)
            if dribble_event:
                events.append(self._build_event(current, "dribble", dribble_event))

            interception_event = self._detect_interception(window)
            if interception_event:
                events.append(self._build_event(current, "interception", interception_event))

            pressing_event = self._detect_pressing(window)
            if pressing_event:
                events.append(self._build_event(current, "pressing", pressing_event))

            counter_event = self._detect_counter_attack(window)
            if counter_event:
                events.append(self._build_event(current, "counter_attack", counter_event))

        return events

    def compute_possession(self, frames: List[Dict[str, Any]]) -> Tuple[Dict[str, float], List[Dict[str, Any]]]:
        """Compute team possession percentages and possession segments.

        Uses closest-player-to-ball heuristic with a distance threshold.
        Possession time is approximated using timestamp_seconds deltas.
        """
        team_time: Dict[str, float] = {}
        segments: List[Dict[str, Any]] = []
        if not frames:
            return {}, []

        last_team = None
        segment_start = None
        last_ts = None

        for frame in frames:
            ts = frame.get("timestamp_seconds")
            possession = self._detect_possession(frame)
            team = possession.get("team") if possession else None

            if last_ts is not None and team is not None:
                delta = max(0.0, float(ts - last_ts)) if ts is not None else 0.0
                team_time[team] = team_time.get(team, 0.0) + delta

            if team != last_team:
                if last_team is not None and segment_start is not None:
                    segments.append(
                        {
                            "team": last_team,
                            "start": segment_start,
                            "end": frame.get("timestamp_match_clock"),
                        }
                    )
                segment_start = frame.get("timestamp_match_clock")

            last_team = team
            last_ts = ts

        if last_team is not None and segment_start is not None:
            segments.append(
                {
                    "team": last_team,
                    "start": segment_start,
                    "end": frames[-1].get("timestamp_match_clock"),
                }
            )

        total_time = sum(team_time.values()) or 1.0
        possession_summary = {team: (time / total_time) * 100 for team, time in team_time.items()}
        return possession_summary, segments

    def save_events(self, events: Dict[str, Any], output_path: str) -> None:
        """Save detected events and possession data to disk as JSON.

        Args:
            events: Dict containing events, possession_summary, possession_segments.
            output_path: Destination JSON file path.
        """
        path = Path(output_path)
        if path.suffix == "":
            path = path.with_suffix(".json")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(events, indent=2), encoding="utf-8")

    def _build_event(self, frame: Dict[str, Any], event: str, info: Dict[str, Any]) -> Dict[str, Any]:
        """Construct a standardized event dict with timestamp info."""
        return {
            "timestamp": frame.get("timestamp_match_clock"),
            "timestamp_seconds": frame.get("timestamp_seconds"),
            "event": event,
            "team": info.get("team", "unknown"),
            "player": info.get("player", "unknown"),
            "confidence": info.get("confidence", 0.5),
        }

    # -----------------------------
    # Helper Functions
    # -----------------------------

    def _get_ball_position(self, frame: Dict[str, Any]) -> Optional[Tuple[float, float]]:
        """Extract ball position from frame data."""
        ball = frame.get("ball")
        if isinstance(ball, dict) and "bbox" in ball:
            x, y, w, h = ball["bbox"]
            return (x + w / 2.0, y + h / 2.0)
        return None

    def _compute_ball_speed(self, frame_t: Dict[str, Any], frame_tm1: Dict[str, Any]) -> Optional[float]:
        """Compute ball speed between two frames using timestamp_seconds."""
        p1 = self._get_ball_position(frame_t)
        p0 = self._get_ball_position(frame_tm1)
        t1 = frame_t.get("timestamp_seconds")
        t0 = frame_tm1.get("timestamp_seconds")
        if p1 is None or p0 is None or t1 is None or t0 is None or t1 == t0:
            return None
        dx = p1[0] - p0[0]
        dy = p1[1] - p0[1]
        dist = (dx * dx + dy * dy) ** 0.5
        return dist / (t1 - t0)

    def _compute_ball_direction(self, frame_t: Dict[str, Any], frame_tm1: Dict[str, Any]) -> Optional[Tuple[float, float]]:
        """Compute normalized ball direction vector between two frames."""
        p1 = self._get_ball_position(frame_t)
        p0 = self._get_ball_position(frame_tm1)
        if p1 is None or p0 is None:
            return None
        dx = p1[0] - p0[0]
        dy = p1[1] - p0[1]
        norm = (dx * dx + dy * dy) ** 0.5
        if norm == 0:
            return None
        return (dx / norm, dy / norm)

    def _detect_possession(self, frame: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Detect which player has possession based on closest distance to ball."""
        ball_pos = self._get_ball_position(frame)
        players = frame.get("players", [])
        if ball_pos is None or not players:
            return None

        closest = None
        min_dist = None
        for player in players:
            bbox = player.get("bbox")
            if not bbox:
                continue
            x, y, w, h = bbox
            player_pos = (x + w / 2.0, y + h / 2.0)
            dx = player_pos[0] - ball_pos[0]
            dy = player_pos[1] - ball_pos[1]
            dist = (dx * dx + dy * dy) ** 0.5
            if min_dist is None or dist < min_dist:
                min_dist = dist
                closest = player

        if min_dist is None or min_dist > self.possession_distance:
            return None

        return {"player_id": closest.get("track_id"), "team": closest.get("team", "unknown")}

    # -----------------------------
    # Heuristic Event Detectors
    # -----------------------------

    def _detect_shot(self, window: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Heuristic shot detection using ball speed and direction."""
        if len(window) < 2:
            return None
        speed = self._compute_ball_speed(window[-1], window[-2])
        if speed is None or speed < 8.0:
            return None
        return {"confidence": min(1.0, speed / 15.0), "team": "unknown"}

    def _detect_pass(self, window: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Heuristic pass detection using possession change within same team."""
        if len(window) < 2:
            return None
        prev_poss = self._detect_possession(window[-2])
        curr_poss = self._detect_possession(window[-1])
        if not prev_poss or not curr_poss:
            return None
        if prev_poss["player_id"] != curr_poss["player_id"] and prev_poss["team"] == curr_poss["team"]:
            return {"team": curr_poss["team"], "confidence": 0.6}
        return None

    def _detect_dribble(self, window: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Heuristic dribble detection based on continuous possession."""
        if len(window) < 3:
            return None
        poss_ids = [self._detect_possession(f) for f in window[-3:]]
        if any(p is None for p in poss_ids):
            return None
        player_ids = [p["player_id"] for p in poss_ids]
        if len(set(player_ids)) == 1:
            return {"team": poss_ids[-1]["team"], "confidence": 0.5}
        return None

    def _detect_interception(self, window: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Heuristic interception detection based on possession change between teams."""
        if len(window) < 2:
            return None
        prev_poss = self._detect_possession(window[-2])
        curr_poss = self._detect_possession(window[-1])
        if not prev_poss or not curr_poss:
            return None
        if prev_poss["team"] != curr_poss["team"]:
            return {"team": curr_poss["team"], "confidence": 0.7}
        return None

    def _detect_pressing(self, window: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Heuristic pressing detection based on nearby defenders."""
        frame = window[-1]
        ball_pos = self._get_ball_position(frame)
        players = frame.get("players", [])
        if ball_pos is None or not players:
            return None

        close_players = 0
        for player in players:
            bbox = player.get("bbox")
            if not bbox:
                continue
            x, y, w, h = bbox
            player_pos = (x + w / 2.0, y + h / 2.0)
            dx = player_pos[0] - ball_pos[0]
            dy = player_pos[1] - ball_pos[1]
            dist = (dx * dx + dy * dy) ** 0.5
            if dist < self.possession_distance * 1.5:
                close_players += 1

        if close_players >= 3:
            return {"confidence": 0.5, "team": "unknown"}
        return None

    def _detect_counter_attack(self, window: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Heuristic counter-attack detection.

        Looks for possession change followed by rapid ball movement.
        """
        if len(window) < 3:
            return None
        prev_poss = self._detect_possession(window[-3])
        curr_poss = self._detect_possession(window[-1])
        speed = self._compute_ball_speed(window[-1], window[-2])
        if prev_poss and curr_poss and prev_poss["team"] != curr_poss["team"] and speed and speed > 6.0:
            return {"team": curr_poss["team"], "confidence": min(1.0, speed / 12.0)}
        return None
