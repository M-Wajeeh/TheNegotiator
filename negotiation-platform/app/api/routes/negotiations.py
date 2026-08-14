from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any
import uuid
from pydantic import BaseModel
import logging

from langgraph.checkpoint.memory import MemorySaver

logger = logging.getLogger(__name__)

try:
    from langgraph.checkpoint.postgres import PostgresSaver
    from psycopg_pool import ConnectionPool
except ImportError:
    PostgresSaver = None
    ConnectionPool = None

from app.core.database import get_db
from app.graph.build_graph import graph
from app.config import settings

router = APIRouter()

pool = None
if ConnectionPool is not None:
    pool = ConnectionPool(conninfo=settings.DATABASE_URL.replace("postgresql+asyncpg", "postgresql"))


def get_checkpointer():
    if PostgresSaver is not None and pool is not None:
        return PostgresSaver(pool)
    logger.warning("Falling back to in-memory checkpointer because psycopg/libpq is unavailable.")
    return MemorySaver()

class StartNegotiationRequest(BaseModel):
    dummy_payload: dict[str, Any]

@router.post("/")
async def create_negotiation(req: StartNegotiationRequest, db: AsyncSession = Depends(get_db)):
    negotiation_id = uuid.uuid4()
    
    checkpointer = get_checkpointer()
    with checkpointer:
        checkpointer.setup()
        app = graph.compile(checkpointer=checkpointer)
        
        initial_state = {
            "negotiation_id": negotiation_id,
            "status": "intake"
        }
        
        config = {"configurable": {"thread_id": str(negotiation_id)}}
        
        # Invoke the graph
        app.invoke(initial_state, config=config)
        
    return {"negotiation_id": str(negotiation_id)}

@router.get("/{id}")
async def get_negotiation(id: uuid.UUID):
    checkpointer = get_checkpointer()
    with checkpointer:
        app = graph.compile(checkpointer=checkpointer)
        config = {"configurable": {"thread_id": str(id)}}
        state = app.get_state(config)
        if not state:
            raise HTTPException(status_code=404, detail="Negotiation not found")
        return state.values

@router.post("/{id}/approve")
async def approve_negotiation(id: uuid.UUID):
    checkpointer = get_checkpointer()
    with checkpointer:
        app = graph.compile(checkpointer=checkpointer)
        config = {"configurable": {"thread_id": str(id)}}
        state = app.get_state(config)
        if not state:
            raise HTTPException(status_code=404, detail="Negotiation not found")
        
        # Resume the graph by passing None to the interrupt point
        app.invoke(None, config=config)
    return {"status": "resumed"}
