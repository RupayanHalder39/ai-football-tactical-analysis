"""Response schemas for the API."""

from typing import Any, List
from pydantic import BaseModel


class FrameResult(BaseModel):
    """Per-frame result placeholder."""

    frame_id: int
    players: List[Any]
    ball: Any


class VideoAnalysisResponse(BaseModel):
    """Top-level video analysis response."""

    frames: List[FrameResult]
