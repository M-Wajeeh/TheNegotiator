import logging
import uuid
import json
from app.graph.state import NegotiationState
from app.schemas.core import BusinessSchema
from app.tools.tavily_client import search_businesses
from app.tools.openai_client import generate_structured_output
from app.agents.prompts.business_discovery import BUSINESS_DISCOVERY_SYSTEM_PROMPT
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class CandidateListSchema(BaseModel):
    candidates: list[BusinessSchema]

async def business_discovery_node(state: NegotiationState):
    logger.info("Executing business_discovery_node")
    
    req = state.get("requirement")
    if not req or not getattr(req, "service_type", None) or not getattr(req, "location", None):
        logger.warning("Missing requirement or location for business discovery")
        return {"status": "failed", "errors": [{"node": "business_discovery", "error": "Missing requirement"}]}
        
    try:
        # Search real businesses
        search_results = await search_businesses(req.service_type, req.location)
        
        # De-duplicate and parse using LLM
        structured_candidates = await generate_structured_output(
            system_prompt=BUSINESS_DISCOVERY_SYSTEM_PROMPT,
            user_prompt=json.dumps(search_results),
            response_format=CandidateListSchema
        )
        
        # Ensure unique IDs for graph tracking
        for c in structured_candidates.candidates:
            if not c.business_id:
                c.business_id = str(uuid.uuid4())
                
        return {
            "status": "planning" if structured_candidates.candidates else "done", # If no candidates, we might want to fail or end
            "candidate_businesses": structured_candidates.candidates
        }
    except Exception as e:
        logger.error(f"Business discovery node failed: {e}")
        return {
            "status": "failed",
            "errors": [{"node": "business_discovery", "error": str(e)}]
        }
