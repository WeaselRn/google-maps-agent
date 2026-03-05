"""
Route Tools
Functions for route calculation and coordinate sampling.
Uses Google Directions API for routing.
"""

import os
import httpx
import polyline as polyline_codec

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
DIRECTIONS_URL = "https://maps.googleapis.com/maps/api/directions/json"


async def get_route(origin: str, destination: str) -> dict:
    """
    Calculate a route between origin and destination using Google Directions API.

    Args:
        origin: Starting location (address or lat,lng string)
        destination: End location (address or lat,lng string)

    Returns:
        dict with keys: path (list of {lat,lng}), distance, duration,
                        duration_seconds, origin_lat, origin_lng,
                        dest_lat, dest_lng
    """
    params = {
        "origin": origin,
        "destination": destination,
        "key": GOOGLE_MAPS_API_KEY,
        "mode": "driving",
    }

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(DIRECTIONS_URL, params=params)
        response.raise_for_status()
        data = response.json()

    if data.get("status") != "OK" or not data.get("routes"):
        return {
            "path": None,
            "distance": None,
            "duration": None,
            "duration_seconds": 0,
            "error": data.get("status", "NO_ROUTES"),
        }

    route = data["routes"][0]
    leg = route["legs"][0]

    # Decode the overview polyline to get the route path
    encoded_polyline = route["overview_polyline"]["points"]
    decoded_coords = polyline_codec.decode(encoded_polyline)
    path = [{"lat": lat, "lng": lng} for lat, lng in decoded_coords]

    distance = leg["distance"]["text"]
    duration = leg["duration"]["text"]
    duration_seconds = leg["duration"]["value"]

    origin_loc = leg["start_location"]
    dest_loc = leg["end_location"]

    return {
        "path": path,
        "distance": distance,
        "duration": duration,
        "duration_seconds": duration_seconds,
        "origin_lat": origin_loc["lat"],
        "origin_lng": origin_loc["lng"],
        "dest_lat": dest_loc["lat"],
        "dest_lng": dest_loc["lng"],
    }


def sample_route_coordinates(path: list[dict] | None, max_samples: int = 10) -> list[dict]:
    """
    Sample coordinates along a route from path coordinates.

    Args:
        path: List of {lat, lng} dicts from Google Directions
        max_samples: Maximum number of sample points (default 10)

    Returns:
        List of dicts with keys: lat, lng
    """
    if not path:
        return []

    if len(path) <= max_samples:
        return path

    step = max(1, len(path) // max_samples)
    sampled = path[::step][:max_samples]
    return sampled
