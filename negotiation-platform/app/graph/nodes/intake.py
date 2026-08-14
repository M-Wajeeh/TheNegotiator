import logging
from app.graph.state import NegotiationState
from app.schemas.core import RequirementSchema
from app.agents.prompts.intake import INTAKE_SYSTEM_PROMPT
from app.tools.openai_client import generate_structured_output
import asyncio

logger = logging.getLogger(__name__)

async def intake_node(state: NegotiationState):
    logger.info("Executing intake_node")
    
    # In a real scenario, we'd have a user input history in the state.
    # We will simulate a user message for now.
    user_input = "I need movers in New York for a 2 bedroom apartment."
    
    try:
        requirement = await generate_structured_output(
            system_prompt=INTAKE_SYSTEM_PROMPT,
            user_prompt=user_input,
            response_format=RequirementSchema
        )
        
        return {
            "status": "intake" if not requirement.is_complete else "discovering",
            "requirement": requirement
        }
    except Exception as e:
        logger.error(f"Intake node failed: {e}")
        return {
            "status": "failed",
            "errors": [{"node": "intake", "error": str(e)}]
        }
