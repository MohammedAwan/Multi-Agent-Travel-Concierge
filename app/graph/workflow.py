from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.graph.state import TravelAgentState
from app.graph.nodes import researcher_node, itinerary_generator_node, tools

builder = StateGraph(TravelAgentState)
def create_travel_graph(checkpointer: AsyncPostgresSaver):
    """Builds and compiles the multi-agent graph backed by PostgreSQL checkpointer."""
    

    builder.add_node("researcher", researcher_node)
    builder.add_node("tools", ToolNode(tools))
    builder.add_node("itinerary_generator", itinerary_generator_node)

    builder.add_edge(START, "researcher")
    builder.add_conditional_edges(
        "researcher",
        tools_condition,
        {"tools": "tools", END: "itinerary_generator"}
    )
    builder.add_edge("tools", "itinerary_generator")
    builder.add_edge("itinerary_generator", END)

    return builder.compile(checkpointer=checkpointer)