from typing import TypedDict, Annotated, Sequence, Optional
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from app.schemas.itinerary import StructuredItinerary

class TravelAgentState(TypedDict):
    # Appends new messages automatically to the thread history
    messages: Annotated[Sequence[BaseMessage], add_messages]
    
    # Form input parameters
    destination: str
    duration: int
    travel_dates: str
    accommodation: str
    budget: str
    interests: str
    pace: str
    dietary_restrictions: str
    special_requests: str
    
    # Output container
    final_itinerary: Optional[StructuredItinerary]