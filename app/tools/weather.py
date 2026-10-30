import os
import httpx
from langchain_core.tools import tool

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

@tool
async def get_live_weather(destination: str) -> str:
    """
    Fetch current live weather conditions and temperature for a given city or destination.
    Use this to adapt daily plans according to climate and expected rainfall.
    """
    if not OPENWEATHER_API_KEY:
        return f"Weather for {destination}: Mostly clear, 22°C (Fallback: OPENWEATHER_API_KEY not set)."

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": destination, "appid": OPENWEATHER_API_KEY, "units": "metric"}

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                weather_desc = data["weather"][0]["description"]
                temp = data["main"]["temp"]
                feels_like = data["main"]["feels_like"]
                humidity = data["main"]["humidity"]
                return (
                    f"Live weather in {destination}: {weather_desc.capitalize()}, "
                    f"Temperature: {temp}°C (feels like {feels_like}°C), Humidity: {humidity}%."
                )
            return f"Weather data unavailable for '{destination}' (HTTP {resp.status_code})."
    except Exception as exc:
        return f"Weather lookup failed for '{destination}': {str(exc)}"