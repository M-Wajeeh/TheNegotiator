import logging
from tavily import AsyncTavilyClient

from app.config import settings

logger = logging.getLogger(__name__)

def get_tavily_client():
    api_key = settings.TAVILY_API_KEY or "dummy-key-for-now"
    return AsyncTavilyClient(api_key=api_key)

async def search_businesses(query: str, location: str):
    client = get_tavily_client()
    try:
        search_query = f"{query} near {location} with phone numbers"
        response = await client.search(search_query, search_depth="advanced", max_results=5)
        return response
    except Exception as e:
        logger.error(f"Failed to search businesses: {e}")
        raise
