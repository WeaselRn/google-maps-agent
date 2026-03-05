"""
Places Tools
Functions for searching places using Google Places Nearby Search API.
"""

import os
import httpx

from tools.routes import get_route, sample_route_coordinates

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
PLACES_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

# Mapping from common place types to Google Places types
PLACE_TYPE_MAP = {
    "restaurant": "restaurant",
    "cafe": "cafe",
    "gas_station": "gas_station",
    "fuel": "gas_station",
    "tourist_attraction": "tourist_attraction",
    "hotel": "lodging",
    "hospital": "hospital",
    "pharmacy": "pharmacy",
    "parking": "parking",
    "supermarket": "supermarket",
}


async def _geocode(location_str: str) -> dict | None:
    """
    Geocode a location string to lat/lng using Google Find Place API.
    Uses the Places API (already enabled) instead of the Geocoding API.

    Args:
        location_str: An address or place name (e.g. "Fort Kochi")

    Returns:
        dict with lat, lng — or None if geocoding fails
    """
    # Check if already in lat,lng format
    parts = location_str.split(",")
    if len(parts) == 2:
        try:
            return {"lat": float(parts[0].strip()), "lng": float(parts[1].strip())}
        except ValueError:
            pass

    # Use Find Place from Text (part of Places API)
    find_place_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    params = {
        "input": location_str,
        "inputtype": "textquery",
        "fields": "geometry",
        "key": GOOGLE_MAPS_API_KEY,
    }
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(find_place_url, params=params)
        response.raise_for_status()
        data = response.json()

    if data.get("status") != "OK" or not data.get("candidates"):
        return None

    loc = data["candidates"][0]["geometry"]["location"]
    return {"lat": loc["lat"], "lng": loc["lng"]}


async def search_places(location: str, place_type: str) -> list[dict]:
    """
    Search for nearby places at a specific location using Google Places API.

    Args:
        location: A location string (address, place name, or "lat,lng")
        place_type: Type of place (e.g. restaurant, cafe, gas_station)

    Returns:
        List of place dicts with keys: name, lat, lng, rating, place_id, address
    """
    # Geocode the location string to get coordinates
    coords = await _geocode(location)
    if not coords:
        return []

    google_type = PLACE_TYPE_MAP.get(place_type, place_type)

    params = {
        "location": f"{coords['lat']},{coords['lng']}",
        "radius": 1500,
        "type": google_type,
        "key": GOOGLE_MAPS_API_KEY,
    }

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(PLACES_URL, params=params)
        response.raise_for_status()
        data = response.json()

    if data.get("status") not in ("OK", "ZERO_RESULTS"):
        return []

    results = []
    for place in data.get("results", []):
        loc = place.get("geometry", {}).get("location", {})
        results.append({
            "name": place.get("name", "Unknown"),
            "lat": loc.get("lat", 0),
            "lng": loc.get("lng", 0),
            "rating": place.get("rating"),
            "place_id": place.get("place_id", ""),
            "address": place.get("vicinity", ""),
        })

    return results


async def search_places_near_point(location: str, place_type: str) -> list[dict]:
    """
    Search for places near a location point.

    Args:
        location: A location string (address, place name, or "lat,lng")
        place_type: Type of place to search for

    Returns:
        List of place dicts
    """
    return await search_places(location, place_type)


async def search_places_along_route(
    origin: str, destination: str, place_type: str
) -> list[dict]:
    """
    Find places along a route by sampling coordinates and searching near each.

    Steps:
    1. get_route(origin, destination) via Google Directions API
    2. sample_route_coordinates(path)
    3. search_places_near_point for each sample
    4. Merge and deduplicate results by place_id
    5. Calculate detour for each result
    6. Rank results by score

    Args:
        origin: Starting location
        destination: End location
        place_type: Type of place to search for

    Returns:
        List of ranked place dicts with detour_minutes
    """
    from tools.detour import calculate_detour

    route = await get_route(origin, destination)

    if not route.get("path"):
        return []

    samples = sample_route_coordinates(route["path"])
    if not samples:
        return []

    all_places: list[dict] = []
    seen_ids: set[str] = set()

    for coord in samples:
        # Convert dict to "lat,lng" string for search_places
        coord_str = f"{coord['lat']},{coord['lng']}"
        places = await search_places_near_point(coord_str, place_type)
        for p in places:
            pid = p.get("place_id")
            if pid and pid not in seen_ids:
                seen_ids.add(pid)
                detour = await calculate_detour(
                    origin, destination, p, route.get("duration_seconds", 0)
                )
                p["detour_minutes"] = detour
                all_places.append(p)

    # Rank: use rating and detour time
    def rank_score(place: dict) -> float:
        rating = place.get("rating") or 3.0
        detour_min = place.get("detour_minutes") or 1
        return 0.6 * rating + 0.4 * (1.0 / max(detour_min, 0.1))

    all_places.sort(key=rank_score, reverse=True)
    return all_places[:10]
