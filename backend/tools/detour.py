"""
Detour Tools
Functions for calculating detour time, optimizing stops,
and suggesting contextual stops on long journeys.
Uses Google Directions API for routing calculations.
"""

import os
from datetime import datetime

import httpx

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
DIRECTIONS_URL = "https://maps.googleapis.com/maps/api/directions/json"


async def calculate_detour(
    origin: str,
    destination: str,
    place: dict,
    direct_duration_seconds: float,
) -> float:
    """
    Estimate the detour time (in minutes) to visit a place along a route.

    Computes: (origin → place → destination via Google Directions) - direct_duration

    Args:
        origin: Starting location string
        destination: End location string
        place: Place dict with lat, lng
        direct_duration_seconds: Duration of the direct route in seconds

    Returns:
        Detour time in minutes (always >= 0)
    """
    try:
        waypoint = f"{place['lat']},{place['lng']}"
        params = {
            "origin": origin,
            "destination": destination,
            "waypoints": f"via:{waypoint}",
            "key": GOOGLE_MAPS_API_KEY,
            "mode": "driving",
        }

        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(DIRECTIONS_URL, params=params)
            response.raise_for_status()
            data = response.json()

        if data.get("status") != "OK" or not data.get("routes"):
            return 0.0

        # Sum duration across all legs
        total_seconds = sum(
            leg["duration"]["value"] for leg in data["routes"][0]["legs"]
        )
        detour_seconds = total_seconds - direct_duration_seconds
        return max(round(detour_seconds / 60, 1), 0)

    except Exception:
        return 0.0


async def optimize_stops(route: dict, stops: list[dict]) -> dict:
    """
    Return an optimized route that includes the given stops.

    Uses Google Directions API with optimize:true for waypoint optimization.

    Args:
        route: Base route dict with origin/destination info
        stops: List of stop dicts with lat, lng

    Returns:
        Optimized route dict with ordered waypoints
    """
    import polyline as polyline_codec

    if not stops:
        return {
            "path": route.get("path"),
            "distance": route.get("distance"),
            "duration": route.get("duration"),
            "ordered_stops": stops,
        }

    try:
        origin = f"{route.get('origin_lat')},{route.get('origin_lng')}"
        destination = f"{route.get('dest_lat')},{route.get('dest_lng')}"
        waypoints_str = "optimize:true|" + "|".join(
            f"{s['lat']},{s['lng']}" for s in stops
        )

        params = {
            "origin": origin,
            "destination": destination,
            "waypoints": waypoints_str,
            "key": GOOGLE_MAPS_API_KEY,
            "mode": "driving",
        }

        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(DIRECTIONS_URL, params=params)
            response.raise_for_status()
            data = response.json()

        if data.get("status") != "OK" or not data.get("routes"):
            return {
                "path": route.get("path"),
                "distance": route.get("distance"),
                "duration": route.get("duration"),
                "ordered_stops": stops,
            }

        result_route = data["routes"][0]

        # Decode overview polyline
        encoded = result_route["overview_polyline"]["points"]
        decoded = polyline_codec.decode(encoded)
        path = [{"lat": lat, "lng": lng} for lat, lng in decoded]

        # Sum distance and duration across all legs
        total_distance_m = sum(leg["distance"]["value"] for leg in result_route["legs"])
        total_duration_s = sum(leg["duration"]["value"] for leg in result_route["legs"])
        distance_km = round(total_distance_m / 1000, 1)
        duration_min = round(total_duration_s / 60)

        # Reorder stops based on waypoint_order
        waypoint_order = result_route.get("waypoint_order", list(range(len(stops))))
        ordered_stops = [stops[i] for i in waypoint_order]

        return {
            "path": path,
            "distance": f"{distance_km} km",
            "duration": f"{duration_min} mins",
            "ordered_stops": ordered_stops,
        }

    except Exception:
        return {
            "path": route.get("path"),
            "distance": route.get("distance"),
            "duration": route.get("duration"),
            "ordered_stops": stops,
        }


async def suggest_contextual_stops(
    origin: str, destination: str, trip_duration_hours: float
) -> list[dict]:
    """
    Proactively suggest stops based on trip context.

    Rules:
    - trip_duration > 2 hours → suggest rest stops / cafes
    - trip_duration > 3 hours → suggest fuel stations
    - Near meal hours (11-14, 18-21) → suggest restaurants

    Args:
        origin: Starting location
        destination: End location
        trip_duration_hours: Estimated trip duration in hours

    Returns:
        List of suggestion dicts with keys: type, name, lat, lng, detour_minutes
    """
    from tools.places import search_places_along_route

    suggestions: list[dict] = []

    if trip_duration_hours > 2:
        cafes = await search_places_along_route(origin, destination, "cafe")
        for c in cafes[:3]:
            suggestions.append({**c, "type": "rest_stop"})

    if trip_duration_hours > 3:
        fuel = await search_places_along_route(origin, destination, "fuel")
        for f in fuel[:2]:
            suggestions.append({**f, "type": "fuel"})

    hour = datetime.now().hour
    if hour in range(11, 14) or hour in range(18, 21):
        restaurants = await search_places_along_route(origin, destination, "restaurant")
        for r in restaurants[:3]:
            suggestions.append({**r, "type": "meal"})

    return suggestions
