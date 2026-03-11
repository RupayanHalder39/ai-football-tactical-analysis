"""Video processing loop for CV pipeline.

This module provides a reusable class that loads a video, iterates through
frames, runs the CVPipeline per frame, and aggregates results. It is
independent of any web framework and can be used in research scripts or
batch processing.

Example:
    processor = VideoProcessor(frame_skip=2)
    results = processor.process_video(
        "match.mp4",
        match_metadata={"match_id": "UCL_2024_02_14_PSG_BAY"},
        save_path="results/UCL_2024_02_14_PSG_BAY",
        format="json",
        stream_write=False,
        progress_callback=None,
        frame_callback=None,
    )
"""

from __future__ import annotations

from typing import List, Dict, Any, Optional, Union, Tuple

import cv2
import json
from pathlib import Path
import pandas as pd
from datetime import datetime, timezone

from .cv_pipeline import CVPipeline


class VideoProcessor:
    """Process a full video through the CV pipeline.

    Responsibilities:
    - Open a video file with OpenCV.
    - Read frames sequentially.
    - Run CVPipeline on each frame (with optional skipping).
    - Collect and return structured analytics results.
    """

    def __init__(self, frame_skip: int = 0, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the processor.

        Args:
            frame_skip: Number of frames to skip between processed frames.
                For example, frame_skip=2 processes every 3rd frame.
            config: Optional configuration passed into CVPipeline.
        """
        if frame_skip < 0:
            raise ValueError("frame_skip must be >= 0")
        self.frame_skip = frame_skip
        self.pipeline = CVPipeline(config=config)

    def process_video(
        self,
        video_path: str,
        match_metadata: Optional[Dict[str, Any]] = None,
        save_path: Optional[str] = None,
        format: str = "json",
        stream_write: bool = False,
        progress_callback: Optional[Any] = None,
        frame_callback: Optional[Any] = None,
        progress_every: int = 100,
    ) -> Dict[str, Any]:
        """Process a video file and return a structured match dataset.

        Args:
            video_path: Path to the video file.
            match_metadata: Optional match metadata dict. If None, a minimal
                metadata block is generated automatically.
            save_path: Optional path prefix for saving results.
            format: Output format when saving (\"json\" or \"parquet\").
            stream_write: If True, stream frame results to disk in JSONL
                as they are produced instead of keeping them in memory.
            progress_callback: Optional callable invoked every N processed frames
                with progress data (frame_index, timestamp_seconds).
            frame_callback: Optional callable invoked after each processed frame
                with the full frame result dict.
            progress_every: Emit progress callbacks every N processed frames.

        Returns:
            A dictionary containing match metadata and per-frame results.
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError("Unable to open video file.")

        fps = cap.get(cv2.CAP_PROP_FPS)
        if not fps or fps <= 0:
            fps = 0.0

        metadata = self.validate_match_metadata(video_path, match_metadata)
        frames: List[Dict[str, Any]] = []
        frame_index = 0
        processed_count = 0
        jsonl_path: Optional[Path] = None
        jsonl_handle = None

        if stream_write:
            if save_path is None:
                raise ValueError("save_path is required when stream_write=True")
            if format.lower().strip() not in {"jsonl", "json"}:
                raise ValueError("stream_write only supports JSONL output")
            jsonl_path, jsonl_handle = self._open_jsonl(save_path, metadata)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Skip frames for performance if configured.
            if self.frame_skip > 0 and (frame_index % (self.frame_skip + 1) != 0):
                frame_index += 1
                continue

            try:
                result = self.pipeline.process_frame(frame)
                result["frame_index"] = frame_index
                if fps > 0:
                    timestamp_seconds = frame_index / fps
                    minutes = int(timestamp_seconds // 60)
                    seconds = int(timestamp_seconds % 60)
                    result["timestamp_seconds"] = float(timestamp_seconds)
                    result["timestamp_match_clock"] = f"{minutes:02d}:{seconds:02d}"
                else:
                    result["timestamp_seconds"] = None
                    result["timestamp_match_clock"] = None

                if stream_write and jsonl_handle is not None:
                    jsonl_handle.write(json.dumps(result) + "\n")
                else:
                    frames.append(result)

                if frame_callback is not None:
                    frame_callback(result)

                processed_count += 1
                if progress_callback is not None and processed_count % max(1, progress_every) == 0:
                    progress_callback(
                        {
                            "frame_index": frame_index,
                            "timestamp_seconds": result.get("timestamp_seconds"),
                        }
                    )
            except Exception:
                # Fail-safe: skip bad frames without crashing the full video job.
                pass

            frame_index += 1

        cap.release()
        if jsonl_handle is not None:
            jsonl_handle.close()

        dataset = {"match_metadata": metadata, "frames": frames}

        if save_path is not None and not stream_write:
            self.save_results(dataset, save_path, format=format)
        return dataset

    def validate_match_metadata(self, video_path: str, match_metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate or auto-generate match metadata.

        Required fields:
            - match_id

        If metadata is None, a minimal block is generated from the video filename.
        """
        if match_metadata is None:
            video_name = Path(video_path).stem
            return {
                "match_id": video_name,
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }

        if not match_metadata.get("match_id"):
            raise ValueError("match_id is required in match_metadata")

        return match_metadata

    def _open_jsonl(self, save_path: str, metadata: Dict[str, Any]) -> Tuple[Path, Any]:
        """Open a JSONL file and write metadata as the first line.

        JSONL format:
            Line 1: {"match_metadata": {...}}
            Line 2+: {"frame_index": ..., "players": [...], ...}
        """
        path = Path(save_path)
        if path.suffix == "":
            path = path.with_suffix(".jsonl")

        path.parent.mkdir(parents=True, exist_ok=True)
        handle = path.open("w", encoding="utf-8")
        handle.write(json.dumps({"match_metadata": metadata}) + "\n")
        return path, handle

    def save_results(self, results: Union[List[Dict[str, Any]], Dict[str, Any]], output_path: str, format: str = "json") -> None:
        """Persist results to disk in JSON or Parquet format.

        Args:
            results: Structured dataset with match metadata and frames.
                A legacy list of frames is also accepted for compatibility.
            output_path: File path without extension or with desired extension.
            format: \"json\" or \"parquet\".

        Raises:
            ValueError: If an unsupported format is provided.
        """
        fmt = format.lower().strip()
        path = Path(output_path)
        if path.suffix == "":
            if fmt == "json":
                path = path.with_suffix(".json")
            elif fmt == "parquet":
                path = path.with_suffix(".parquet")

        path.parent.mkdir(parents=True, exist_ok=True)

        if fmt == "json":
            with path.open("w", encoding="utf-8") as f:
                json.dump(results, f, indent=2)
        elif fmt == "parquet":
            # Streaming is not supported for Parquet in this module.
            # Flatten frame-level data. Attach metadata as columns for filtering.
            if isinstance(results, dict) and "frames" in results:
                frames = results.get("frames", [])
                df = pd.json_normalize(frames)
                metadata = results.get("match_metadata", {})
                for key, value in metadata.items():
                    df[f"match_{key}"] = value
            else:
                df = pd.DataFrame(results)
            df.to_parquet(path, index=False)
        else:
            raise ValueError(f"Unsupported format: {format}")
