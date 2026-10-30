from pydantic import BaseModel, Field
from typing import List

class ActivityItem(BaseModel):
    time_slot: str = Field(description="Morning, Afternoon, Evening, or specific time")
    activity_name: str = Field(description="Landmark, attraction, or venue name")
    description: str = Field(description="Practical details, transit tips, and highlights")
    estimated_cost: str = Field(description="Estimated cost in USD or 'Free'")

class MealRecommendation(BaseModel):
    meal_type: str = Field(description="Breakfast, Lunch, or Dinner")
    cuisine: str = Field(description="Cuisine style adhering to dietary preferences")
    suggested_spot: str = Field(description="Specific restaurant or area recommendation")

class DaySchedule(BaseModel):
    day_number: int = Field(description="1, 2, 3, etc.")
    theme: str = Field(description="E.g., Historic Old Town & Street Markets")
    activities: List[ActivityItem]
    meals: List[MealRecommendation]
    day_summary: str = Field(description="Logistics and overview for the day")

class StructuredItinerary(BaseModel):
    destination: str
    trip_summary: str = Field(description="High-level overview, pacing strategy, and climate/packing note")
    daily_plans: List[DaySchedule]
    estimated_total_cost: str = Field(description="Estimated total budget breakdown")
    local_tips: List[str] = Field(description="Essential transit, safety, and cultural advice")

    def to_markdown_text(self) -> str:
        """
        Converts the structured object back to markdown text so the original 
        frontend JS expecting {'itinerary': '...'} renders seamlessly.
        """
        lines = [f"# Travel Itinerary: {self.destination}", f"{self.trip_summary}\n"]
        for day in self.daily_plans:
            lines.append(f"## Day {day.day_number}: {day.theme}")
            lines.append(f"*{day.day_summary}*\n")
            lines.append("### Activities")
            for act in day.activities:
                lines.append(f"- **{act.time_slot}**: {act.activity_name} ({act.estimated_cost}) — {act.description}")
            lines.append("\n### Dining Recommendations")
            for meal in day.meals:
                lines.append(f"- **{meal.meal_type}**: {meal.suggested_spot} ({meal.cuisine})")
            lines.append("\n" + "-" * 40)
        
        lines.append(f"\n### Estimated Total Budget: {self.estimated_total_cost}")
        lines.append("\n### Important Local Tips")
        for tip in self.local_tips:
            lines.append(f"- {tip}")
        return "\n".join(lines)