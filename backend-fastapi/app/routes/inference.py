"""Inference routes for video analysis.

This module defines public API endpoints for asynchronous video analysis.
The workflow creates a job, processes the video in a background task,
and returns job status via polling.
"""

import json
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile

from app.pipelines.video_pipeline import process_video
from app.services.job_service import create_job, get_job, save_result, save_upload, update_job_status

router = APIRouter()


@router.post("/analyze-video")
async def analyze_video(background_tasks: BackgroundTasks, file: UploadFile = File(...)) -> dict:
    """Create a new analysis job for an uploaded video.

    Steps:
    1) Save the uploaded video to disk.
    2) Create a job record in SQLite.
    3) Launch background processing.
    4) Return the job ID immediately.
    """
    video_bytes = await file.read()
    video_path = save_upload(video_bytes, file.filename or "upload.mp4")
    job = create_job(video_path)

    def _run_job(job_id: str, video_path_: str) -> None:
        """Background task wrapper to process video and update job state."""
        try:
            update_job_status(job_id, "processing")
            result = process_video(video_path_, match_id=job_id)
            if hasattr(result, "dict"):
                result = result.dict()
            result_path = save_result(job_id, result)
            update_job_status(job_id, "completed", result_path=result_path)
        except Exception:
            update_job_status(job_id, "failed")

    background_tasks.add_task(_run_job, job.job_id, job.video_path)

    return {"job_id": job.job_id}


@router.get("/job-status/{job_id}")
async def job_status(job_id: str) -> dict:
    """Return the current status of a job by ID."""
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"job_id": job.job_id, "status": job.status}


@router.get("/job-result/{job_id}")
async def job_result(job_id: str) -> dict:
    """Return the analysis result for a completed job.

    Behavior:
    - 404 if the job does not exist.
    - Returns {"status": "processing"} if the job is not completed.
    - Returns the JSON result for completed jobs.
    """
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != "completed":
        return {"status": "processing"}

    if not job.result_path:
        raise HTTPException(status_code=500, detail="Job result path missing")

    result_path = Path(job.result_path)
    if not result_path.exists():
        raise HTTPException(status_code=500, detail="Job result file not found")

    try:
        return json.loads(result_path.read_text())
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=500, detail="Invalid result JSON") from exc
