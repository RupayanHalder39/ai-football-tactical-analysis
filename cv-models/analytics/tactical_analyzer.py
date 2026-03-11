"""Tactical analytics module.

Provides basic analytics derived from tracked player positions in pitch
coordinates. These metrics are useful for performance analysis and
tactical insights such as speed, distance covered, team centroid, and
heatmaps.
"""

from typing import Dict, List, Tuple, Any

import numpy as np


class TacticalAnalyzer:
    """Compute simple tactical metrics from tracked positions.

    This class maintains lightweight state across frames to estimate
    per-player speed and accumulated distance.
    """

    def __init__(self, fps: float = 25.0) -> None:
        """Initialize analyzer.

        Args:
            fps: Frames per second for speed/distance calculations.
        """
        self.fps = fps
        self.previous_positions: Dict[int, Tuple[float, float]] = {}
        self.total_distance: Dict[int, float] = {}

    def compute_metrics(self, tracked_players: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compute all tactical metrics for a single frame.

        Args:
            tracked_players: List of tracked players with pitch coordinates.

        Returns:
            Dictionary containing speed, distance, and team centroid metrics.
        """
        player_speed = self.compute_player_speed(tracked_players)
        distance_covered = self.compute_distance_covered(tracked_players)
        team_centroid = self.compute_team_centroid(tracked_players)

        return {
            "player_speed": player_speed,
            "distance_covered": distance_covered,
            "team_centroid": team_centroid,
        }

    def compute_player_speed(self, tracked_players: List[Dict[str, Any]]) -> Dict[int, float]:
        """Estimate player speed based on frame-to-frame displacement.

        Uses last known positions to compute instantaneous speed in m/s.
        """
        speeds: Dict[int, float] = {}
        for player in tracked_players:
            track_id = player.get("track_id")
            pitch_coord = player.get("pitch_coord") or player.get("pitch_point")
            if track_id is None or pitch_coord is None:
                continue

            prev = self.previous_positions.get(track_id)
            if prev is None:
                speeds[track_id] = 0.0
            else:
                dist = float(np.linalg.norm(np.array(pitch_coord) - np.array(prev)))
                speeds[track_id] = dist * self.fps

            self.previous_positions[track_id] = tuple(pitch_coord)

        return speeds

    def compute_distance_covered(self, tracked_players: List[Dict[str, Any]]) -> Dict[int, float]:
        """Accumulate distance covered per player over time."""
        for player in tracked_players:
            track_id = player.get("track_id")
            pitch_coord = player.get("pitch_coord") or player.get("pitch_point")
            if track_id is None or pitch_coord is None:
                continue

            prev = self.previous_positions.get(track_id)
            if prev is not None:
                dist = float(np.linalg.norm(np.array(pitch_coord) - np.array(prev)))
                self.total_distance[track_id] = self.total_distance.get(track_id, 0.0) + dist
            else:
                self.total_distance.setdefault(track_id, 0.0)

        return dict(self.total_distance)

    def compute_team_centroid(self, tracked_players: List[Dict[str, Any]]) -> Dict[str, Tuple[float, float]]:
        """Compute average team position for tactical structure analysis."""
        team_positions: Dict[str, List[Tuple[float, float]]] = {}
        for player in tracked_players:
            team = player.get("team")
            pitch_coord = player.get("pitch_coord") or player.get("pitch_point")
            if team is None or pitch_coord is None:
                continue
            team_positions.setdefault(team, []).append(tuple(pitch_coord))

        centroids: Dict[str, Tuple[float, float]] = {}
        for team, positions in team_positions.items():
            if not positions:
                continue
            mean = np.mean(np.array(positions), axis=0)
            centroids[team] = (float(mean[0]), float(mean[1]))

        return centroids

    def compute_heatmap(self, positions: List[Tuple[float, float]], bins: Tuple[int, int] = (20, 20)) -> Any:
        """Compute a simple 2D histogram heatmap.

        Args:
            positions: List of (x, y) pitch coordinates.
            bins: Histogram resolution in x and y directions.

        Returns:
            A 2D numpy array representing density of positions.
        """
        if not positions:
            return np.zeros(bins)

        coords = np.array(positions)
        heatmap, _, _ = np.histogram2d(coords[:, 0], coords[:, 1], bins=bins)
        return heatmap
