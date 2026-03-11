"""Job service for managing asynchronous video analysis jobs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import json
import uuid

from app.db.database import get_connection, get_project_root
from app.db.models import init_db


@dataclass
class JobRecord:
    """In-memory representation of a job record."""

    job_id: str
    video_path: str
    status: str
    result_path: str | None
    created_at: str


def _now_iso() -> str:
    """Return current UTC time as ISO string."""
    return datetime.now(timezone.utc).isoformat()


def _results_dir() -> Path:
    """Resolve results directory for job outputs."""
    return get_project_root() / "data" / "results"


def _uploads_dir() -> Path:
    """Resolve uploads directory for incoming videos."""
    return get_project_root() / "data" / "uploads"


def create_job(video_path: str) -> JobRecord:
    """Create a new job record with status 'pending'."""
    init_db()
    job_id = uuid.uuid4().hex
    created_at = _now_iso()

    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO jobs (job_id, video_path, status, result_path, created_at)
            VALUES (?, ?, ?, ?, ?);
            """,
            (job_id, video_path, "pending", None, created_at),
        )
        conn.commit()
    finally:
        conn.close()

    return JobRecord(
        job_id=job_id,
        video_path=video_path,
        status="pending",
        result_path=None,
        created_at=created_at,
    )


def update_job_status(job_id: str, status: str, result_path: str | None = None) -> None:
    """Update job status (and optionally result path)."""
    init_db()
    conn = get_connection()
    try:
        conn.execute(
            """
            UPDATE jobs
            SET status = ?, result_path = COALESCE(?, result_path)
            WHERE job_id = ?;
            """,
            (status, result_path, job_id),
        )
        conn.commit()
    finally:
        conn.close()


def get_job(job_id: str) -> JobRecord | None:
    """Fetch a job record by ID."""
    init_db()
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT job_id, video_path, status, result_path, created_at FROM jobs WHERE job_id = ?;",
            (job_id,),
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        return None

    return JobRecord(
        job_id=row["job_id"],
        video_path=row["video_path"],
        status=row["status"],
        result_path=row["result_path"],
        created_at=row["created_at"],
    )


def save_result(job_id: str, result: dict) -> str:
    """Persist analysis result to a JSON file and return its path."""
    results_dir = _results_dir()
    results_dir.mkdir(parents=True, exist_ok=True)
    result_path = results_dir / f"{job_id}.json"
    result_path.write_text(json.dumps(result, indent=2))
    return str(result_path)


def save_upload(video_bytes: bytes, filename: str) -> str:
    """Save uploaded video bytes to disk and return the file path."""
    uploads_dir = _uploads_dir()
    uploads_dir.mkdir(parents=True, exist_ok=True)
    safe_name = Path(filename).name or "upload.mp4"
    file_path = uploads_dir / f"{uuid.uuid4().hex}_{safe_name}"
    file_path.write_bytes(video_bytes)
    return str(file_path)
