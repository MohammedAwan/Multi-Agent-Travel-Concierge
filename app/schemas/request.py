from pydantic import BaseModel, Field
from typing import Optional
import uuid

class TravelFormRequest(BaseModel):
    destination: str = Field(..., min_length=2, description="Target city or country")
    duration: int = Field(..., ge=1, le=30, description="Duration in days")
    travel_dates: Optional[str] = Field(default="Flexible", description="Dates or travel season")
    accommodation: Optional[str] = Field(default="Standard Hotel", description="Hostel, Hotel, Airbnb, Luxury Resort")
    budget: Optional[str] = Field(default="Moderate", description="Budget tier or limit")
    interests: Optional[str] = Field(default="Sightseeing, Food", description="User interests/activities")
    pace: Optional[str] = Field(default="Moderate", description="Relaxed, Moderate, or Fast-paced")
    dietary_restrictions: Optional[str] = Field(default="None", description="Dietary restrictions or preferences")
    special_requests: Optional[str] = Field(default="None", description="Accessibility, family-friendly, etc.")
    
    # Client session identifier to track multi-turn iterations per trip
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
class ChatFollowUpRequest(BaseModel):
    session_id: str
    message: str
    current_itinerary: str 