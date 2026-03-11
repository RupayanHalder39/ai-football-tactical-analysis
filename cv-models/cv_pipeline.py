"""Central computer vision pipeline for football analytics.

This module orchestrates detection, tracking, ball detection, pitch
keypoints, homography, team classification, and tactical analytics for
individual frames. It is designed to be reusable as a standalone library
and independent of the FastAPI backend.
"""

from __future__ import annotations

from typing import Dict, Any, List, Optional, Tuple

from .detection.player_detector import PlayerDetector
from .tracking.player_tracker import PlayerTracker
from .detection.ball_detector import BallDetector
from .pitch.pitch_keypoint_detector import PitchKeypointDetector
from .pitch.pitch_homography import PitchHomography
from .pitch_mapper import PitchMapper
from .team.team_classifier import TeamClassifier
from .analytics.tactical_analyzer import TacticalAnalyzer


class CVPipeline:
    """Orchestrates the full CV stack for a single football frame.

    Pipeline stages:
    1) Player detection
    2) Player tracking
    3) Ball detection
    4) Pitch keypoint detection
    5) Homography estimation
    6) Pitch coordinate mapping
    7) Team classification
    8) Tactical analytics

    Each stage is optional and robust to missing detections.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize pipeline modules.

        Args:
            config: Optional configuration dict passed to submodules.
        """
        cfg = config or {}
        self.player_detector = PlayerDetector(cfg.get("player_detector"))
        self.player_tracker = PlayerTracker(cfg.get("player_tracker"))
        self.ball_detector = BallDetector(cfg.get("ball_detector"))
        self.pitch_keypoint_detector = PitchKeypointDetector(cfg.get("pitch_keypoint_detector"))
        self.pitch_homography = PitchHomography(cfg.get("pitch_points"))
        self.team_classifier = TeamClassifier(cfg.get("team_classifier"))
        self.tactical_analyzer = TacticalAnalyzer(cfg.get("fps", 25.0))

    def _bottom_center(self, bbox: List[float]) -> Tuple[float, float]:
        """Compute bottom-center point of a bounding box.

        Args:
            bbox: [x, y, w, h]

        Returns:
            (x_center, y_bottom)
        """
        x, y, w, h = bbox
        return (x + w / 2.0, y + h)

    def process_frame(self, frame) -> Dict[str, Any]:
        """Process a single frame through the full pipeline.

        Args:
            frame: A video frame as a numpy array.

        Returns:
            Dictionary with tracked players, ball detections,
            team labels, and analytics outputs.
        """
        # 1) Player detection.
        players = self.player_detector.detect(frame) or []

        # 2) Player tracking.
        tracked_players = self.player_tracker.update(players) if players else []

        # 3) Ball detection.
        ball = self.ball_detector.detect(frame) or []

        # 4) Pitch keypoint detection.
        pitch_keypoints = self.pitch_keypoint_detector.detect(frame) or {}

        # 5) Homography estimation (requires at least 4 keypoints).
        homography = None
        if pitch_keypoints:
            homography = self.pitch_homography.compute_homography(pitch_keypoints)

        # 6) Map pixel coordinates to pitch coordinates (if homography available).
        pitch_mapper = PitchMapper(homography)
        if homography is not None:
            tracked_players = pitch_mapper.transform_players(tracked_players)
            for player in tracked_players:
                if player.get("pitch_x") is not None and player.get("pitch_y") is not None:
                    player["pitch_point"] = (player["pitch_x"], player["pitch_y"])
                else:
                    player["pitch_point"] = None
        else:
            for player in tracked_players:
                if "bbox" in player:
                    pixel_point = self._bottom_center(player["bbox"])
                    player["x"] = pixel_point[0]
                    player["y"] = pixel_point[1]
                player["pitch_x"] = None
                player["pitch_y"] = None
                player["pitch_point"] = None

        # Map ball detections to pitch coordinates (keep both list and primary).
        ball_detections: List[Dict[str, Any]] = []
        if ball:
            for det in ball:
                if isinstance(det, dict):
                    ball_detections.append(pitch_mapper.transform_ball(det))
        ball_primary = ball_detections[0] if ball_detections else None

        # 7) Team classification.
        team_labels = self.team_classifier.classify(tracked_players, frame) if tracked_players else []

        # 8) Tactical analytics.
        analytics = {}
        if hasattr(self.tactical_analyzer, "compute_metrics"):
            # If a unified metrics method exists in the future, prefer it.
            analytics = self.tactical_analyzer.compute_metrics(tracked_players)
        else:
            # Placeholder minimal analytics structure for now.
            analytics = {
                "player_speed": {},
                "distance_covered": {},
                "team_centroid": {},
            }

        return {
            "players": tracked_players,
            "ball": ball_primary,
            "ball_detections": ball_detections,
            "teams": team_labels,
            "analytics": analytics,
        }
