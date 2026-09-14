"""Top-level FastAPI entrypoint for uvicorn runner and Docker container."""
from app.main import app

__all__ = ["app"]
