from fastapi import APIRouter
import uuid
import logging
from app.api.routes.negotiations import get_checkpointer
from app.graph.build_graph import graph

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/{id}")
async def list_quotes(id: uuid.UUID):
    try:
        checkpointer = get_checkpointer()
        with checkpointer:
            compiled = graph.compile(checkpointer=checkpointer)
            config = {"configurable": {"thread_id": str(id)}}
            state = compiled.get_state(config)
            if state and state.values:
                quotes = state.values.get("quotes", [])
                return {"quotes": quotes}
    except Exception as e:
        logger.warning(f"Failed to fetch quotes for {id}: {e}")
    return {"quotes": []}
