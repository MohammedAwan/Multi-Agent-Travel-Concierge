import pytest
from pydantic import ValidationError
from app.schemas.request import TravelFormRequest
from app.schemas.itinerary import StructuredItinerary, DaySchedule, ActivityItem, MealRecommendation

def test_travel_form_request_defaults_and_coercion():
    # Test valid defaults when only required field is passed
    req = TravelFormRequest(destination="Tokyo", duration=5)
    assert req.destination == "Tokyo"
    assert req.duration == 5
    assert req.accommodation == "Standard Hotel"

def test_duration_string_and_invalid_coercion():
    # String duration from HTML form
    req_str = TravelFormRequest(destination="Rome", duration="4")
    assert req_str.duration == 4

    # Boundary enforcement (below min or above max)
    req_min = TravelFormRequest(destination="Rome", duration=0)
    assert req_min.duration == 1  # Clamped to 1

    req_max = TravelFormRequest(destination="Rome", duration=99)
    assert req_max.duration == 30  # Clamped to 30

def test_structured_itinerary_markdown_formatter():
    itinerary = StructuredItinerary(
        destination="Kyoto",
        trip_summary="A wonderful cultural exploration.",
        daily_plans=[
            DaySchedule(
                day_number=1,
                theme="Temples & Gardens",
                activities=[
                    ActivityItem(
                        time_slot="Morning",
                        activity_name="Kinkaku-ji",
                        description="Golden Pavilion visit",
                        estimated_cost="$5"
                    )
                ],
                meals=[
                    MealRecommendation(
                        meal_type="Lunch",
                        cuisine="Ramen",
                        suggested_spot="Ippudo"
                    )
                ],
                day_summary="Explored north Kyoto."
            )
        ],
        estimated_total_cost="$150",
        local_tips=["Buy an IC bus card."]
    )

    md = itinerary.to_markdown_text()
    assert "# Travel Itinerary: Kyoto" in md
    assert "Kinkaku-ji" in md
    assert "Ippudo" in md