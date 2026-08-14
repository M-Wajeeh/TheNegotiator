from langgraph.graph import StateGraph, START, END
from app.graph.state import NegotiationState
from langgraph.constants import Send

from app.graph.nodes.intake import intake_node
from app.graph.nodes.document_parser import document_parser_node
from app.graph.nodes.business_discovery import business_discovery_node
from app.graph.nodes.call_planning import call_planning_node
from app.graph.nodes.vendor_flow import vendor_graph, VendorState
from app.graph.nodes.quote_analysis import quote_analysis_node
from app.graph.nodes.recommendation import recommendation_node
from app.graph.nodes.report import report_node

def route_intake(state: NegotiationState):
    req = state.get("requirement")
    if not req:
        return "intake"
    is_complete = req.is_complete if hasattr(req, "is_complete") else req.get("is_complete", False)
    if not is_complete:
        return "intake"
    return "document_parser"

def route_discovery(state: NegotiationState):
    if not state.get("candidate_businesses"):
        return END
    return "call_planning"

def route_call_planning(state: NegotiationState):
    # Fan out to vendor flow for each candidate
    return [Send("vendor_flow", {"business_id": biz.business_id}) for biz in state.get("candidate_businesses", [])]

def route_recommendation(state: NegotiationState):
    if state.get("requires_human_approval"):
        return "human_gate"
    return "report"

def build_negotiation_graph():
    workflow = StateGraph(NegotiationState)

    workflow.add_node("intake", intake_node)
    workflow.add_node("document_parser", document_parser_node)
    workflow.add_node("business_discovery", business_discovery_node)
    workflow.add_node("call_planning", call_planning_node)
    workflow.add_node("vendor_flow", vendor_graph) # Subgraph
    workflow.add_node("quote_analysis", quote_analysis_node)
    workflow.add_node("recommendation", recommendation_node)
    
    # Human Gate node just passes state but acts as an interrupt point
    def human_gate(state: NegotiationState):
        return {"status": "reporting", "requires_human_approval": False}
        
    workflow.add_node("human_gate", human_gate)
    workflow.add_node("report", report_node)

    # Routing
    workflow.add_edge(START, "intake")
    workflow.add_conditional_edges("intake", route_intake, ["intake", "document_parser"])
    workflow.add_edge("document_parser", "business_discovery")
    workflow.add_conditional_edges("business_discovery", route_discovery, [END, "call_planning"])
    workflow.add_conditional_edges("call_planning", route_call_planning, ["vendor_flow"])
    
    # After all vendor flows complete, they join here
    workflow.add_edge("vendor_flow", "quote_analysis")
    
    workflow.add_edge("quote_analysis", "recommendation")
    workflow.add_conditional_edges("recommendation", route_recommendation, ["human_gate", "report"])
    workflow.add_edge("human_gate", "report")
    workflow.add_edge("report", END)

    return workflow

graph = build_negotiation_graph()
