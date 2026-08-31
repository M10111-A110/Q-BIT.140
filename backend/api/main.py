from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import activities, ai, health

app = FastAPI(
    title="Q-BIT API",
    version="1.0.0",
    description="Q-BIT.140 AI-Based Interactive Quantum Algorithm Learning Platform Gateway",
)

# Enable CORS for local web prototypes and future frontend interfaces
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers
app.include_router(health.router, prefix="/api")
app.include_router(activities.router, prefix="/api")
app.include_router(ai.router, prefix="/api")

# Top-level health check probe
app.include_router(health.router)
