import os
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from app.graph.state import TravelAgentState
from app.schemas.itinerary import StructuredItinerary
from app.tools.weather import get_live_weather
from app.tools.places import search_attractions_and_venues
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SELECTED_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
tools = [get_live_weather, search_attractions_and_venues]

# Base LLM using Groq
llm = ChatGroq(
    model=SELECTED_MODEL,
    groq_api_key=GROQ_API_KEY,
    temperature=0.3
)

llm_with_tools = llm.bind_tools(tools)

async def researcher_node(state: TravelAgentState):
    """Agent 1: Checks live weather and searches verified attractions matching preferences."""
    system_prompt = (
        "You are an expert travel researcher. Call your tools to fetch live weather "
        "and top attractions for the destination matching the user's interests. "
        "Do not invent facts; query your tools."
    )
    user_query = (
        f"Fetch live weather and verified attractions for {state['destination']} "
        f"matching interests: '{state['interests']}'."
    )
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_query)]
    response = await llm_with_tools.ainvoke(messages)
    return {"messages": [response]}

async def itinerary_generator_node(state: TravelAgentState):
    """Generates a complete travel itinerary formatted directly in Markdown."""
    system_prompt = SystemMessage(
        content=(
            "You are an expert travel concierge. Synthesize the user's travel details "
            "and any gathered research into a comprehensive, high-quality itinerary.\n\n"
            "Formatting Guidelines:\n"
            "- Use clean Markdown (# for destination, ## for Day X, ### for activities).\n"
            "- Include estimated costs, daily summaries, and specific timing for morning, afternoon, and evening.\n"
            "- Do NOT wrap your output in a JSON code block or call any tools. Output pure Markdown text."
        )
    )

    user_prompt = HumanMessage(
        content=(
            f"Generate a {state['duration']}-day travel itinerary for {state['destination']}.\n"
            f"- Travel Dates: {state.get('travel_dates', 'Flexible')}\n"
            f"- Budget Level: {state.get('budget', 'Moderate')}\n"
            f"- Accommodation Preference: {state.get('accommodation', 'Hotel')}\n"
            f"- Interests & Style: {state.get('interests', 'Sightseeing')}\n"
            f"- Pace: {state.get('pace', 'Moderate')}\n"
            f"- Dietary Preferences: {state.get('dietary_restrictions', 'None')}\n"
            f"- Special Requests: {state.get('special_requests', 'None')}"
        )
    )

    # Invoke LLM directly (avoids tool schema parsing issues)
    response = await llm.ainvoke([system_prompt, user_prompt])

    return {
        "messages": [response],
        "final_itinerary": response.content
    }


async def chat_refiner_node(state: TravelAgentState):
    """Refines or answers questions about the itinerary based on conversation history."""
    system_prompt = SystemMessage(
        content=(
            "You are an expert travel concierge. The user has generated an itinerary "
            "and may ask for adjustments, extra recommendations, or questions. "
            "Modify the plan or answer while maintaining the destination context. "
            "Format responses using clean Markdown."
        )
    )
    
    # Passes entire multi-turn message history automatically
    conversation = [system_prompt] + list(state["messages"])
    response = await llm.ainvoke(conversation)
    
    return {
        "messages": [response],
        "final_itinerary": response.content
    }