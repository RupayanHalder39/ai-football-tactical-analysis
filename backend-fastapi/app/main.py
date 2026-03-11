"""FastAPI application entry point.

Includes CORS middleware so the Vite dev server can call the API.
Allowed origins are configurable via the ALLOWED_ORIGINS env var.
"""

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
import os

from app.routes.inference import router as inference_router
from backend.api.events import router as events_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(title="Football Tactical Analysis API", version="0.1.0")

    # CORS configuration for frontend dev server and future origins.
    # Set ALLOWED_ORIGINS as a comma-separated list to override defaults.
    raw_origins = os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173")
    allowed_origins = [o.strip() for o in raw_origins.split(",") if o.strip()]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(inference_router, tags=["inference"])
    app.include_router(events_router, tags=["events"])

    return app


app = create_app()
