"""Team classification via jersey color clustering.

This module assigns players to teams based on jersey colors extracted
from their bounding boxes. A common baseline is KMeans clustering on the
upper portion of each player's crop.
"""

from typing import Dict, List, Any

import numpy as np
from sklearn.cluster import KMeans


class TeamClassifier:
    """Assign team labels using dominant jersey colors."""

    def __init__(self, config: Dict[str, Any] | None = None) -> None:
        """Initialize classifier with optional configuration.

        Args:
            config: Optional settings such as number of clusters.
        """
        self.config = config or {}
        self.n_clusters = int(self.config.get("n_clusters", 2))

    def _extract_jersey_patch(self, frame, bbox: List[float]) -> np.ndarray:
        """Extract the jersey region from a player bounding box.

        This uses the upper half of the box as a proxy for jersey pixels.
        """
        x, y, w, h = [int(v) for v in bbox]
        x1 = max(0, x)
        y1 = max(0, y)
        x2 = max(0, x + w)
        y2 = max(0, y + h)

        crop = frame[y1:y2, x1:x2]
        if crop.size == 0:
            return crop

        return crop[: max(1, crop.shape[0] // 2), :]

    def classify(self, players: List[Dict[str, Any]], frame) -> List[Dict[str, Any]]:
        """Assign team labels based on jersey color clustering.

        Args:
            players: Tracked player dicts containing track_id and bbox.
            frame: Current video frame.

        Returns:
            List of dicts: {"track_id": int, "team": "team_1"|"team_2"}
        """
        if not players:
            return []

        jersey_colors = []
        valid_players = []
        for player in players:
            patch = self._extract_jersey_patch(frame, player["bbox"])
            if patch.size == 0:
                continue
            pixels = patch.reshape(-1, 3)
            jersey_colors.append(np.mean(pixels, axis=0))
            valid_players.append(player)

        if not jersey_colors:
            return []

        kmeans = KMeans(n_clusters=self.n_clusters, n_init=10, random_state=0)
        labels = kmeans.fit_predict(np.array(jersey_colors))

        results = []
        for player, label in zip(valid_players, labels):
            results.append({"track_id": player.get("track_id"), "team": f"team_{label + 1}"})

        return results
