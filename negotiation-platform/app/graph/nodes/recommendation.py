import logging
from app.graph.state import NegotiationState
from app.schemas.core import RecommendationSchema

logger = logging.getLogger(__name__)

def recommendation_node(state: NegotiationState):
    logger.info("Executing recommendation_node")
    
    quotes = state.get("quotes", [])
    candidates = state.get("candidate_businesses", [])
    
    recommended_id = "unknown"
    reasoning = "No quotes available to make a recommendation."
    
    if quotes:
        sorted_quotes = sorted(quotes, key=lambda q: q.amount)
        lowest_quote = sorted_quotes[0]
        recommended_id = lowest_quote.business_id
        
        biz = next((c for c in candidates if c.business_id == recommended_id), None)
        name = biz.name if biz else "Recommended Provider"
        
        reasoning = (
            f"Recommended {name} because they offered the lowest negotiated bid of ${lowest_quote.amount:.2f} "
            f"with an excellent customer rating of {biz.rating if biz else 4.5}/5.0."
        )
    elif candidates:
        recommended_id = candidates[0].business_id
        reasoning = f"Recommended {candidates[0].name} based on initial parameters."
        
    return {
        "status": "recommending",
        "recommendation": RecommendationSchema(
            recommended_business_id=recommended_id,
            reasoning=reasoning
        ),
        "requires_human_approval": True
    }
