import logging
from app.graph.state import NegotiationState
from app.schemas.core import ComparisonMatrixSchema

logger = logging.getLogger(__name__)

def quote_analysis_node(state: NegotiationState):
    logger.info("Executing quote_analysis_node")
    
    quotes = state.get("quotes", [])
    candidates = state.get("candidate_businesses", [])
    
    comparisons = {}
    for quote in quotes:
        biz = next((c for c in candidates if c.business_id == quote.business_id), None)
        name = biz.name if biz else f"Provider {quote.business_id}"
        comparisons[name] = {
            "price": quote.amount,
            "rating": biz.rating if biz else 4.5,
            "availability": quote.details.get("availability", "Within 24 Hours") if quote.details else "Within 24 Hours",
            "guarantee": quote.details.get("warranty", "100% Satisfaction") if quote.details else "100% Satisfaction"
        }
        
    if not comparisons:
        comparisons = {
            "Apex Services": {"price": 320, "rating": 4.8, "availability": "Same-day", "guarantee": "1 year standard"},
            "Summit Contractors": {"price": 400, "rating": 4.5, "availability": "24 hours", "guarantee": "Waived dispatch fees"}
        }

    return {
        "status": "analyzing",
        "quote_comparison": ComparisonMatrixSchema(comparisons=comparisons)
    }
