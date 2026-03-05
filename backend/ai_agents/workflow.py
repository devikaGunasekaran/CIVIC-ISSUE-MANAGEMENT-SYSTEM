from langgraph.graph import StateGraph, END
from typing import TypedDict
from ai_agents.agents import (
    transcription_agent, translation_agent, vision_agent,
    geo_agent, rag_agent, reasoning_agent, routing_agent
)

class GraphState(TypedDict):
    text: str
    voice: str
    image: str
    gps: str
    geo: dict
    rag: str
    issue: str
    priority: str
    reason: str
    department: str
    eta: str

def build_langgraph():
    graph = StateGraph(GraphState)

    graph.add_node("transcription", transcription_agent)
    graph.add_node("translation", translation_agent)
    graph.add_node("vision", vision_agent)
    graph.add_node("geo", geo_agent)
    graph.add_node("rag", rag_agent)
    graph.add_node("reason", reasoning_agent)
    graph.add_node("route", routing_agent)

    graph.set_entry_point("transcription")
    graph.add_edge("transcription", "translation")
    graph.add_edge("translation", "vision")
    graph.add_edge("vision", "geo")
    graph.add_edge("geo", "rag")
    graph.add_edge("rag", "reason")
    graph.add_edge("reason", "route")
    graph.add_edge("route", END)

    return graph.compile()