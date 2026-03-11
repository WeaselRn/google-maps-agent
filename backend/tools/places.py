"""
Places Tools
Functions for searching places using Google Places Nearby Search API.
"""

import os
import httpx

from tools.routes import get_route, sample_route_coordinates

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
PLACES_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"


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
    "atm": "atm",
    "metro": "subway_station",
    "metro_station": "subway_station",
    "train": "train_station",
    "train_station": "train_station",
    "charging": "electric_vehicle_charging_station",
}


async def _geocode(location_str: str):

    parts = location_str.split(",")

    if len(parts) == 2:
        try:
            return {"lat": float(parts[0]), "lng": float(parts[1])}
        except:
            pass

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

    if data.get("status") != "OK":
        return None

    loc = data["candidates"][0]["geometry"]["location"]

    return {"lat": loc["lat"], "lng": loc["lng"]}


async def search_places(location: str, place_type: str):

    coords = await _geocode(location)

    if not coords:
        return []

    google_type = PLACE_TYPE_MAP.get(place_type)

    params = {
        "location": f"{coords['lat']},{coords['lng']}",
        "radius": 1500,
        "key": GOOGLE_MAPS_API_KEY,
    }

    if google_type:
        params["type"] = google_type
    else:
        params["keyword"] = place_type

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
            "lat": loc.get("lat"),
            "lng": loc.get("lng"),
            "rating": place.get("rating"),
            "place_id": place.get("place_id"),
            "address": place.get("vicinity"),
        })

    return results


async def search_places_near_point(location: str, place_type: str):

    return await search_places(location, place_type)


async def search_places_along_route(origin: str, destination: str, place_type: str):

    from tools.detour import calculate_detour

    route = await get_route(origin, destination)

    samples = sample_route_coordinates(route["path"])

    seen_ids = set()
    results = []

    for coord in samples:

        coord_str = f"{coord['lat']},{coord['lng']}"

        places = await search_places_near_point(coord_str, place_type)

        for p in places:

            pid = p.get("place_id")

            if pid and pid not in seen_ids:

                seen_ids.add(pid)

                detour = await calculate_detour(
                    origin,
                    destination,
                    p,
                    route.get("duration_seconds", 0),
                )

                p["detour_minutes"] = detour

                results.append(p)

    def rank_score(place):

        rating = place.get("rating") or 3
        detour = place.get("detour_minutes") or 1

        return 0.6 * rating + 0.4 * (1 / max(detour, 0.1))

    results.sort(key=rank_score, reverse=True)

    return results[:10]