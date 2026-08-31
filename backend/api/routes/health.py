from __future__ import annotations

from fastapi import APIRouter
from ..schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def get_health() -> HealthResponse:
    """Health check endpoint confirming API availability."""
    return HealthResponse(status="ok", service="qbit-api")
