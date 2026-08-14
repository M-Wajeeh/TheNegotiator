from fastapi import APIRouter

from app.tools.elevenlabs_client import elevenlabs_enabled
router = APIRouter()

@router.post("/interview")
async def start_interview():
    return {"status": "interview started", "elevenlabs_configured": elevenlabs_enabled()}

@router.post("/webhook")
async def voice_webhook(payload: dict):
    return {"status": "webhook received", "elevenlabs_configured": elevenlabs_enabled()}
