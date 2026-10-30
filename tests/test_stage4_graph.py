import pytest
from unittest.mock import AsyncMock, patch
from langchain_core.messages import AIMessage
from app.graph.nodes import researcher_node
from app.schemas.itinerary import StructuredItinerary, DaySchedule

@pytest.mark.asyncio
async def test_researcher_node_execution():
    state = {
        "messages": [],
        "destination": "Seoul",
        "interests": "Street Food",
        "duration": 3,
        "travel_dates": "Spring",
        "accommodation": "Hotel",
        "budget": "Moderate",
        "pace": "Moderate",
        "dietary_restrictions": "None",
        "special_requests": "None",
        "final_itinerary": None
    }

    mock_llm_response = AIMessage(content="Checked weather and food spots for Seoul.")

    with patch("app.graph.nodes.llm_with_tools.ainvoke", new=AsyncMock(return_value=mock_llm_response)):
        output = await researcher_node(state)
        assert "messages" in output
        assert len(output["messages"]) == 1
        assert output["messages"][0].content == "Checked weather and food spots for Seoul."