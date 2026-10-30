import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_home_page_serves_auth_html(async_client):
    response = await async_client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Sign In" in response.text

@pytest.mark.asyncio
async def test_planner_page_serves_index_html(async_client):
    response = await async_client.get("/planner")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

@pytest.mark.asyncio
async def test_generate_itinerary_unauthorized_without_jwt(async_client):
    payload = {"destination": "Berlin", "duration": 2}
    response = await async_client.post("/generate_itinerary", json=payload)
    # Must reject without Bearer token
    assert response.status_code in [401, 403]

@pytest.mark.asyncio
async def test_generate_itinerary_with_valid_jwt(async_client, valid_jwt_token):
    payload = {
        "destination": "Cairo",
        "duration": 3,
        "budget": "Budget",
        "interests": "History"
    }

    mock_itinerary_dict = {
        "destination": "Cairo",
        "trip_summary": "Pyramids and Old Cairo trip.",
        "daily_plans": [],
        "estimated_total_cost": "$200",
        "local_tips": ["Stay hydrated."]
    }

    class MockStructuredResult:
        def to_markdown_text(self):
            return "# Travel Itinerary: Cairo\nPyramids tour."
        def model_dump(self):
            return mock_itinerary_dict

    mock_state = {"final_itinerary": MockStructuredResult()}

    with patch("app.main.travel_graph.ainvoke", new=AsyncMock(return_value=mock_state)):
        response = await async_client.post(
            "/generate_itinerary",
            json=payload,
            headers={"Authorization": f"Bearer {valid_jwt_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "itinerary" in data
        assert "Pyramids tour" in data["itinerary"]
        assert "structured_data" in data