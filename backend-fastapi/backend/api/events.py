"""Event and possession API endpoints.

These endpoints expose match events and possession analytics derived from
JSON files produced by EventEngine.save_events(). The API intentionally
reads precomputed results to avoid coupling request latency to CV/ML work.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import json
import os

from fastapi import APIRouter, HTTPException

router = APIRouter()


def _project_root() -> Path:
    """Resolve the monorepo project root.

    events.py lives at: backend-fastapi/backend/api/events.py
    so the project root is three levels up from this file.
    """
    return Path(__file__).resolve().parents[3]


def _candidate_results_dirs() -> List[Path]:
    """Return ordered candidate results directories.

    Priority:
    1) EVENT_RESULTS_DIR env var (explicit override)
    2) Project root results/ (where pipeline writes outputs)
    3) backend-fastapi/results/ (backward compatibility)
    4) CWD/results (last-resort fallback)
    """
    env_dir = os.environ.get("EVENT_RESULTS_DIR")
    if env_dir:
        return [Path(env_dir)]

    project_root = _project_root()
    return [
        project_root / "results",
        project_root / "backend-fastapi" / "results",
        Path.cwd() / "results",
    ]


def _load_latest_events_file() -> Dict[str, Any]:
    """Load the most recent *_events.json file from the results directory.

    Returns:
        Parsed JSON content as a dict.
    """
    results_dir = None
    for candidate in _candidate_results_dirs():
        if candidate.exists():
            results_dir = candidate
            break

    if results_dir is None:
        raise HTTPException(status_code=404, detail="Results directory not found")

    candidates = sorted(results_dir.glob("*_events.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not candidates:
        raise HTTPException(status_code=404, detail="No event result files found")

    try:
        return json.loads(candidates[0].read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=500, detail="Invalid events JSON") from exc


@router.get("/events")
def get_events() -> List[Dict[str, Any]]:
    """Return detected match events.

    Response format:
        [
          {"timestamp": "02:14", "event": "pass", "confidence": 0.83},
          {"timestamp": "02:18", "event": "shot", "confidence": 0.91}
        ]
    """
    data = _load_latest_events_file()
    return data.get("events", [])


@router.get("/possession")
def get_possession() -> Dict[str, float]:
    """Return match possession percentages by team."""
    data = _load_latest_events_file()
    return data.get("possession_summary", {})


@router.get("/possession-timeline")
def get_possession_timeline() -> List[Dict[str, Any]]:
    """Return possession timeline segments.

    Response format:
        [
          {"team": "PSG", "start": "02:11", "end": "03:45"},
          {"team": "Bayern", "start": "03:45", "end": "04:12"}
        ]
    """
    data = _load_latest_events_file()
    return data.get("possession_segments", [])
