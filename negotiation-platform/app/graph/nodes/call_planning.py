import logging
import json
from app.graph.state import NegotiationState
from app.schemas.core import CallPlanSchema
from app.agents.prompts.call_planning import CALL_PLANNING_SYSTEM_PROMPT
from app.tools.openai_client import generate_structured_output

logger = logging.getLogger(__name__)

async def call_planning_node(state: NegotiationState):
    logger.info("Executing call_planning_node")
    
    req = state.get("requirement")
    candidates = state.get("candidate_businesses", [])
    
    context = {
        "requirement": req.model_dump() if req else {},
        "candidates": [c.model_dump() for c in candidates]
    }
    
    try:
        call_plan = await generate_structured_output(
            system_prompt=CALL_PLANNING_SYSTEM_PROMPT,
            user_prompt=json.dumps(context),
            response_format=CallPlanSchema
        )
        
        return {
            "status": "calling",
            "call_plan": call_plan
        }
    except Exception as e:
        logger.error(f"Call planning node failed: {e}")
        return {
            "status": "failed",
            "errors": [{"node": "call_planning", "error": str(e)}]
        }
