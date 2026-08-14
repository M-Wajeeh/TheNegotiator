import logging

from app.config import settings

logger = logging.getLogger(__name__)


def get_elevenlabs_api_key() -> str | None:
    return settings.ELEVENLABS_API_KEY


def elevenlabs_enabled() -> bool:
    return bool(get_elevenlabs_api_key())