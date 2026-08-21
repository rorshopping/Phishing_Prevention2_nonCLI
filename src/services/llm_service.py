import json
import logging
from typing import Any

from openai import AsyncOpenAI

from src.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = "You are a cybersecurity simulation strategist. Return ONLY valid JSON."


class LLMService:
    def __init__(self) -> None:
        self.llm = AsyncOpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
            timeout=60.0,
            max_retries=0,  # callers handle retries/fallbacks
        )

    async def _complete(self, messages: list[dict[str, str]]) -> str:
        response = await self.llm.chat.completions.create(
            model=settings.llm_model,
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
        )
        return (response.choices[0].message.content or "").strip()

    async def structured_generate(self, prompt: str) -> dict[str, Any]:
        try:
            raw = await self._complete([
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ])
            if raw.startswith("```"):
                raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            return json.loads(raw)
        except Exception as e:
            logger.error("LLM structured generation failed: %s", e)
            raise

    async def generate(self, prompt: str) -> str:
        try:
            return await self._complete([
                {"role": "system", "content": "You are a cybersecurity simulation assistant."},
                {"role": "user", "content": prompt},
            ])
        except Exception as e:
            logger.error("LLM generation failed: %s", e)
            raise

    async def chat(self, system_prompt: str, messages: list[dict[str, str]]) -> str:
        llm_messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
        for message in messages:
            if message.get("role") == "user":
                llm_messages.append({"role": "user", "content": message["content"]})
            else:
                llm_messages.append({"role": "assistant", "content": message["content"]})
        try:
            return await self._complete(llm_messages)
        except Exception as e:
            logger.error("LLM chat generation failed: %s", e)
            raise
