import pytest
import respx
from httpx import Response
from app.tools.weather import get_live_weather
from app.tools.places import search_attractions_and_venues

@pytest.mark.asyncio
@respx.mock
async def test_get_live_weather_success():
    respx.get("https://api.openweathermap.org/data/2.5/weather").mock(
        return_value=Response(200, json={
            "weather": [{"description": "scattered clouds"}],
            "main": {"temp": 18.5, "feels_like": 17.8, "humidity": 65}
        })
    )
    result = await get_live_weather.ainvoke({"destination": "London"})
    assert "Scattered clouds" in result
    assert "18.5°C" in result

@pytest.mark.asyncio
@respx.mock
async def test_get_live_weather_failure_fallback():
    respx.get("https://api.openweathermap.org/data/2.5/weather").mock(
        return_value=Response(500)
    )
    result = await get_live_weather.ainvoke({"destination": "InvalidCity"})
    assert "Weather data unavailable" in result or "failed" in result

@pytest.mark.asyncio
async def test_search_attractions_fallback(monkeypatch):
    # Test without OPENTRIPMAP_API_KEY
    monkeypatch.setattr("app.tools.places.OPENTRIPMAP_API_KEY", None)
    result = await search_attractions_and_venues.ainvoke({
        "destination": "Venice",
        "interests": "Gondola, Architecture"
    })
    assert "Fallback" in result