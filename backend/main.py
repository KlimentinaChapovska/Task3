"""
FastAPI backend — exposes weather data from Open-Meteo to the React frontend.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Allow importing the shared package when running from the backend/ directory
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from shared.weather_service import WeatherResult, WeatherServiceError, get_weather

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(title="MADA Demo API", version="1.0.0")

# CORS — in production this list is replaced by the actual frontend origin via
# the ALLOWED_ORIGINS environment variable (comma-separated).
_raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000")
allowed_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class WeatherResponse(BaseModel):
    city: str
    country: str
    latitude: float
    longitude: float
    temperature: float
    unit: str
    condition: str | None


class HealthResponse(BaseModel):
    status: str
    version: str


class ErrorResponse(BaseModel):
    detail: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/api/health", response_model=HealthResponse, tags=["meta"])
async def health() -> HealthResponse:
    """Simple health check used by Docker and deployment platforms."""
    return HealthResponse(status="ok", version="1.0.0")


@app.get(
    "/api/weather",
    response_model=WeatherResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        502: {"model": ErrorResponse},
        504: {"model": ErrorResponse},
    },
    tags=["weather"],
)
async def weather(
    city: str = Query(..., min_length=1, max_length=100, description="City name"),
) -> WeatherResponse:
    """Return current temperature and weather condition for the requested city."""
    try:
        result: WeatherResult = await get_weather(city)
    except WeatherServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))

    return WeatherResponse(
        city=result.city,
        country=result.country,
        latitude=result.latitude,
        longitude=result.longitude,
        temperature=result.temperature,
        unit=result.unit,
        condition=result.condition,
    )
