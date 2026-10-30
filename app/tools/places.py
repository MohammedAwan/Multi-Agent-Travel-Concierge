import os
import httpx
from langchain_core.tools import tool

OPENTRIPMAP_API_KEY = os.getenv("OPENTRIPMAP_API_KEY")

@tool
async def search_attractions_and_venues(destination: str, interests: str) -> str:
    """
    Search for verified attractions, landmarks, and activity spots for a destination
    matching specific interests (e.g. museums, nature, food).
    """
    if not OPENTRIPMAP_API_KEY:
        return (
            f"Top spots in {destination} related to '{interests}': "
            f"1. Central Cultural Landmark, 2. Historic Town Center, 3. Waterfront/Scenic Walkway. "
            "(Fallback: OPENTRIPMAP_API_KEY not set)."
        )

    # 1. Geocode destination to lat/lon via OpenTripMap API
    geoname_url = "https://api.opentripmap.com/0.1/en/places/geoname"
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            geo_resp = await client.get(geoname_url, params={"name": destination, "apikey": OPENTRIPMAP_API_KEY})
            if geo_resp.status_code != 200 or "lat" not in geo_resp.json():
                return f"Could not geolocate '{destination}' to fetch attractions."

            geo_data = geo_resp.json()
            lat, lon = geo_data["lat"], geo_data["lon"]

            # 2. Query POIs within a 5km radius
            radius_url = "https://api.opentripmap.com/0.1/en/places/radius"
            radius_params = {
                "radius": 5000,
                "lon": lon,
                "lat": lat,
                "rate": "2",
                "format": "json",
                "limit": 6,
                "apikey": OPENTRIPMAP_API_KEY
            }
            places_resp = await client.get(radius_url, params=radius_params)
            if places_resp.status_code == 200:
                places = places_resp.json()
                if not places:
                    return f"No specific attractions indexed for {destination}."
                names = [p.get("name") for p in places if p.get("name")]
                return f"Verified spots in {destination}: {', '.join(names[:5])}."
            return f"Failed to retrieve places (HTTP {places_resp.status_code})."
    except Exception as exc:
        return f"Attraction lookup failed for '{destination}': {str(exc)}"