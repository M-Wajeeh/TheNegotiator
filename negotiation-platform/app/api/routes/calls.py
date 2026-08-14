from fastapi import APIRouter
import uuid
import logging
from app.api.routes.negotiations import get_checkpointer
from app.graph.build_graph import graph

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/{id}")
async def list_calls(id: uuid.UUID):
    try:
        checkpointer = get_checkpointer()
        with checkpointer:
            compiled = graph.compile(checkpointer=checkpointer)
            config = {"configurable": {"thread_id": str(id)}}
            state = compiled.get_state(config)
            if state and state.values:
                calls = state.values.get("calls", [])
                return {"calls": calls}
    except Exception as e:
        logger.warning(f"Failed to fetch calls for {id}: {e}")
    return {"calls": []}
