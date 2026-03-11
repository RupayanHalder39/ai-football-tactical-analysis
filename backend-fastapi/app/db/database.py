"""SQLite database utilities for job tracking.

This module centralizes database path resolution and connection helpers.
All paths are resolved relative to the project root to avoid hardcoding.
"""

from pathlib import Path
import sqlite3


def get_project_root() -> Path:
    """Return the backend project root directory.

    This relies on the file location to derive the root path.
    """
    return Path(__file__).resolve().parents[2]


def get_db_path() -> Path:
    """Return the SQLite database file path.

    The location can be overridden via the `JOBS_DB_PATH` environment variable.
    """
    env_path = Path(
        str(
            __import__("os").environ.get(
                "JOBS_DB_PATH",
                get_project_root() / "data" / "jobs.db",
            )
        )
    )
    return env_path


def get_connection() -> sqlite3.Connection:
    """Create a SQLite connection with row access by column name."""
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn
