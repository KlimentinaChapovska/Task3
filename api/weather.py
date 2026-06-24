"""
Vercel serverless function — GET /api/weather?city=<name>

Vercel Python functions use BaseHTTPRequestHandler.
The shared/ directory is on the Python path because it sits at the repo root.
"""

from __future__ import annotations

import asyncio
import json
import sys
import os
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Ensure the repo root (where shared/ lives) is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from shared.weather_service import get_weather, WeatherServiceError


def _json_response(handler: BaseHTTPRequestHandler, status: int, payload: dict) -> None:
    body = json.dumps(payload).encode()
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        city_values = params.get("city", [])

        if not city_values or not city_values[0].strip():
            _json_response(self, 400, {"detail": "Query parameter 'city' is required."})
            return

        city = city_values[0].strip()
        if len(city) > 100:
            _json_response(self, 400, {"detail": "City name is too long."})
            return

        try:
            result = asyncio.run(get_weather(city))
        except WeatherServiceError as exc:
            _json_response(self, exc.status_code, {"detail": str(exc)})
            return
        except Exception as exc:
            _json_response(self, 500, {"detail": f"Internal error: {exc}"})
            return

        _json_response(
            self,
            200,
            {
                "city": result.city,
                "country": result.country,
                "latitude": result.latitude,
                "longitude": result.longitude,
                "temperature": result.temperature,
                "unit": result.unit,
                "condition": result.condition,
            },
        )
