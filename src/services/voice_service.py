import logging
from typing import Any

import httpx

from src.config import settings

logger = logging.getLogger(__name__)


class VoiceService:
    def __init__(self) -> None:
        self.api_key = settings.openai_api_key or settings.llm_api_key
        self.base_url = "https://api.openai.com/v1"
        if settings.llm_base_url and "openai.com" not in settings.llm_base_url and not settings.openai_api_key:
            logger.warning(
                "LLM base URL is not OpenAI (%s) and no OPENAI_API_KEY set. "
                "TTS will likely fail. Set OPENAI_API_KEY in .env for TTS support.",
                settings.llm_base_url,
            )

    async def synthesize(self, text: str, voice: str = "alloy") -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    f"{self.base_url}/audio/speech",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": "tts-1",
                        "input": text,
                        "voice": voice,
                        "response_format": "mp3",
                    },
                )
                resp.raise_for_status()
                return {"url": "openai-tts", "format": "mp3", "content_length": len(resp.content)}
        except Exception as e:
            logger.error("Voice synthesis failed: %s", e)
            raise
