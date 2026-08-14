from openai import AsyncOpenAI
import logging

from app.config import settings

logger = logging.getLogger(__name__)

def get_openai_client() -> AsyncOpenAI:
    api_key = settings.OPENAI_API_KEY or "dummy-key-for-now"
    return AsyncOpenAI(api_key=api_key)

async def generate_structured_output(system_prompt: str, user_prompt: str, response_format: type):
    client = get_openai_client()
    try:
        response = await client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format=response_format,
        )
        return response.choices[0].message.parsed
    except Exception as e:
        logger.error(f"Failed to generate structured output: {e}")
        raise

async def analyze_document_with_vision(system_prompt: str, image_url: str, response_format: type):
    client = get_openai_client()
    try:
        response = await client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                },
            ],
            response_format=response_format,
            max_tokens=1500,
        )
        return response.choices[0].message.parsed
    except Exception as e:
        logger.error(f"Failed to analyze document: {e}")
        raise
