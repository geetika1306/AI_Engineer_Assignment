import os

import aiohttp

from utils.retry import retry_async


class LLMError(Exception):
    pass


async def call_groq(
    session,
    prompt
):
    """
    Groq-only LLM provider.
    """

    api_key = os.getenv(
        "GROQ_API_KEY"
    )

    if not api_key:
        raise LLMError(
            "GROQ_API_KEY not configured"
        )

    url = (
        "https://api.groq.com/openai/"
        "v1/chat/completions"
    )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0
    }

    async def request():

        async with session.post(
            url,
            headers=headers,
            json=payload,
            timeout=aiohttp.ClientTimeout(
                total=60
            )
        ) as response:

            if response.status == 429:
                raise LLMError(
                    "429 Rate Limited"
                )

            if response.status == 413:
                raise LLMError(
                    "413 Payload Too Large"
                )

            if response.status == 401:
                raise LLMError(
                    "401 Unauthorized"
                )

            response.raise_for_status()

            data = await response.json()

            return data[
                "choices"
            ][0][
                "message"
            ][
                "content"
            ]

    return await retry_async(
    request,
    retries=6,
    base_delay=30
)