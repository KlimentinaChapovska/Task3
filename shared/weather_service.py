"""
Shared weather service — calls Open-Meteo Geocoding + Forecast APIs.
Used by both the FastAPI backend and the Streamlit app.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import httpx

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# WMO Weather Interpretation Codes (subset)
WMO_DESCRIPTIONS: dict[int, str] = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Icy fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    80: "Slight showers",
    81: "Moderate showers",
    82: "Violent showers",
    95: "Thunderstorm",
    99: "Thunderstorm with hail",
}


@dataclass
class WeatherResult:
    city: str
    country: str
    latitude: float
    longitude: float
    temperature: float
    unit: str
    condition: Optional[str]


class WeatherServiceError(Exception):
    """Raised when the weather service cannot fulfil a request."""

    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.status_code = status_code


async def get_weather(city: str) -> WeatherResult:
    """Resolve a city name to coordinates, then fetch current temperature."""
    city = city.strip()
    if not city:
        raise WeatherServiceError("City name must not be empty.")

    async with httpx.AsyncClient(timeout=10.0) as client:
        # --- Geocoding ---
        try:
            geo_resp = await client.get(
                GEOCODING_URL,
                params={"name": city, "count": 1, "language": "en", "format": "json"},
            )
            geo_resp.raise_for_status()
        except httpx.TimeoutException:
            raise WeatherServiceError(
                "Geocoding API timed out. Try again.", status_code=504
            )
        except httpx.HTTPError as exc:
            raise WeatherServiceError(
                f"Geocoding API error: {exc}", status_code=502
            )

        geo_data = geo_resp.json()
        results = geo_data.get("results")
        if not results:
            raise WeatherServiceError(
                f"City '{city}' not found. Check the spelling and try again.",
                status_code=404,
            )

        place = results[0]
        lat: float = place["latitude"]
        lon: float = place["longitude"]
        resolved_city: str = place.get("name", city)
        country: str = place.get("country", "")

        # --- Forecast ---
        try:
            wx_resp = await client.get(
                FORECAST_URL,
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "current": "temperature_2m,weathercode",
                    "temperature_unit": "celsius",
                    "timezone": "auto",
                },
            )
            wx_resp.raise_for_status()
        except httpx.TimeoutException:
            raise WeatherServiceError(
                "Forecast API timed out. Try again.", status_code=504
            )
        except httpx.HTTPError as exc:
            raise WeatherServiceError(
                f"Forecast API error: {exc}", status_code=502
            )

        wx_data = wx_resp.json()
        current = wx_data.get("current", {})
        temperature: float = current.get("temperature_2m", 0.0)
        weathercode: Optional[int] = current.get("weathercode")
        condition = WMO_DESCRIPTIONS.get(weathercode) if weathercode is not None else None

        units = wx_data.get("current_units", {})
        unit: str = units.get("temperature_2m", "°C")

        return WeatherResult(
            city=resolved_city,
            country=country,
            latitude=lat,
            longitude=lon,
            temperature=temperature,
            unit=unit,
            condition=condition,
        )


def get_weather_sync(city: str) -> WeatherResult:
    """Synchronous wrapper — used by Streamlit which runs in a regular thread."""
    import asyncio

    return asyncio.run(get_weather(city))
