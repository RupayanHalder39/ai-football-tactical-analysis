"""Database schema initialization for job tracking."""

from app.db.database import get_connection


def init_db() -> None:
    """Initialize the jobs table if it does not exist."""
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                job_id TEXT PRIMARY KEY,
                video_path TEXT NOT NULL,
                status TEXT NOT NULL,
                result_path TEXT,
                created_at TEXT NOT NULL
            );
            """
        )
        conn.commit()
    finally:
        conn.close()
