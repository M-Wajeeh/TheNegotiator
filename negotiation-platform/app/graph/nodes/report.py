import logging
from app.graph.state import NegotiationState

logger = logging.getLogger(__name__)

def report_node(state: NegotiationState):
    logger.info("Executing report_node")
    neg_id = state.get("negotiation_id", "default")
    return {
        "status": "done",
        "report_url": f"https://negotiation-platform-reports.s3.amazonaws.com/{neg_id}_summary.pdf"
    }
