"""FastAPI application entry point."""

from fastapi import FastAPI

from app.routes.inference import router as inference_router
from backend.api.events import router as events_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(title="Football Tactical Analysis API", version="0.1.0")

    app.include_router(inference_router, tags=["inference"])
    app.include_router(events_router, tags=["events"])

    return app


app = create_app()
