import logging
import uuid
from typing import Literal, TypedDict
from langgraph.graph import StateGraph, START, END
from app.schemas.core import CallRecordSchema, QuoteSchema
from app.config import settings
from app.tools.openai_client import get_openai_client
from app.tools.gmail_client import send_vendor_email, create_email_draft

logger = logging.getLogger(__name__)

class VendorState(TypedDict, total=False):
    business_id: str
    call_outcome: str | None
    email_status: str | None
    email_thread_id: str | None
    call_record: CallRecordSchema | None
    quote: QuoteSchema | None

async def voice_calling_node(state: VendorState):
    biz_id = state.get("business_id", "")
    logger.info(f"Executing voice_calling_node for {biz_id}")
    
    api_key = settings.OPENAI_API_KEY or "dummy-key-for-now"
    if api_key != "dummy-key-for-now" and api_key:
        try:
            client = get_openai_client()
            prompt = f"Generate a realistic short telephone transcript where an AI Agent negotiates rates for a service with provider ID {biz_id}. Agree on a random quote between $250 and $450."
            response = await client.chat.completions.create(
                model="gpt-4o-2024-08-06",
                messages=[
                    {"role": "system", "content": "You are a professional negotiation phone simulator."},
                    {"role": "user", "content": prompt}
                ]
            )
            transcript = response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI transcript generation failed: {e}")
            transcript = f"Agent: Hello, I am calling to secure a competitive rate for service.\nProvider: Sure, our standard rate is $400.\nAgent: Can you offer any volume discount or waive travel fees?\nProvider: Yes, we can discount $80, bringing the total to $320.\nAgent: Excellent! That works well for us."
    else:
        transcript = f"Agent: Hello, I am calling to secure a competitive rate for service.\nProvider: Sure, our standard rate is $400.\nAgent: Can you offer any volume discount or waive travel fees?\nProvider: Yes, we can discount $80, bringing the total to $320.\nAgent: Excellent! That works well for us."

    return {
        "call_outcome": "CONFIRMED_QUOTE",
        "call_record": CallRecordSchema(
            business_id=biz_id,
            call_id=str(uuid.uuid4()),
            status="completed",
            outcome="CONFIRMED_QUOTE",
            transcript=transcript
        )
    }

async def email_negotiation_node(state: VendorState):
    biz_id = state.get("business_id", "")
    logger.info(f"Executing email_negotiation_node for {biz_id}")

    vendor_email = f"sales@{biz_id.lower().replace(' ', '')}.com"
    subject = f"Negotiation Quote Request - Account Ref #{biz_id}"
    body = (
        f"Hello,\n\nWe are looking to secure competitive pricing for our upcoming service requirements. "
        f"Could you please provide your best volume-discounted quote and terms?\n\nBest regards,\nProcurement Team"
    )

    # Dispatch email via Gmail API tool (or simulation)
    result = send_vendor_email(to_email=vendor_email, subject=subject, body_text=body)
    
    return {
        "email_status": result.get("status", "sent"),
        "email_thread_id": result.get("thread_id", str(uuid.uuid4()))
    }

async def negotiation_node(state: VendorState):
    biz_id = state.get("business_id", "")
    logger.info(f"Executing negotiation_node for {biz_id}")
    return {
        "quote": QuoteSchema(
            business_id=biz_id,
            amount=320.0,
            details={"service": "service", "warranty": "1 year standard", "availability": "Same-day"}
        )
    }

def format_output(state: VendorState):
    return {
        "calls": [state["call_record"]] if state.get("call_record") else [],
        "quotes": [state["quote"]] if state.get("quote") else []
    }

def route_vendor(state: VendorState):
    if state.get("call_outcome") == "CALLBACK_SCHEDULED":
        return "voice_calling"
    return "email_negotiation"

builder = StateGraph(VendorState)
builder.add_node("voice_calling", voice_calling_node)
builder.add_node("email_negotiation", email_negotiation_node)
builder.add_node("negotiation", negotiation_node)
builder.add_node("format_output", format_output)

builder.add_edge(START, "voice_calling")
builder.add_conditional_edges("voice_calling", route_vendor)
builder.add_edge("email_negotiation", "negotiation")
builder.add_edge("negotiation", "format_output")
builder.add_edge("format_output", END)

vendor_graph = builder.compile()
