from __future__ import annotations

from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .routes import activities, ai, health

app = FastAPI(
    title="Q-BIT API",
    version="1.0.0",
    description="Q-BIT.140 AI-Based Interactive Quantum Algorithm Learning Platform Gateway",
)

# Enable CORS for local development of any frontend client
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000",
        "*",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Mount API routers (always take precedence)
app.include_router(health.router, prefix="/api")
app.include_router(activities.router, prefix="/api")
app.include_router(ai.router, prefix="/api")

# Top-level health check probe
app.include_router(health.router)

# Mount static frontend directory optionally if present
frontend_dir = Path(__file__).resolve().parent.parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
