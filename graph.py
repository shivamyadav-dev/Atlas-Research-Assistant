from typing import List, Dict, Any, Optional
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END  # type: ignore
from agents import planner_node, search_node, synthesizer_node  # type: ignore

class AtlasState(TypedDict, total=False):
    question: str
    subquestions: List[str]
    search_results: List[Dict[str, Any]]
    final_report: str

sg = StateGraph(AtlasState)
sg.add_node("planner", planner_node)
sg.add_node("search", search_node)
sg.add_node("synthesizer", synthesizer_node)

sg.add_edge(START, "planner")
sg.add_edge("planner", "search")
sg.add_edge("search", "synthesizer")
sg.add_edge("synthesizer", END)

graph = sg.compile()
