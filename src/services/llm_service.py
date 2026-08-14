import json
import logging
from typing import Any

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from src.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = "You are a cybersecurity simulation strategist. Return ONLY valid JSON."


class LLMService:
    def __init__(self) -> None:
        self.llm = ChatOpenAI(
            model=settings.llm_model,
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
            temperature=0.7,
            max_tokens=1024,
        )

    async def structured_generate(self, prompt: str) -> dict[str, Any]:
        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=prompt),
            ])
            raw = response.content.strip()
            if raw.startswith("```"):
                raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            return json.loads(raw)
        except Exception as e:
            logger.error("LLM structured generation failed: %s", e)
            raise

    async def generate(self, prompt: str) -> str:
        try:
            response = await self.llm.ainvoke([
                SystemMessage(content="You are a cybersecurity simulation assistant."),
                HumanMessage(content=prompt),
            ])
            return response.content.strip()
        except Exception as e:
            logger.error("LLM generation failed: %s", e)
            raise

    async def chat(self, system_prompt: str, messages: list[dict[str, str]]) -> str:
        llm_messages = [SystemMessage(content=system_prompt)]
        for message in messages:
            if message.get("role") == "user":
                llm_messages.append(HumanMessage(content=message["content"]))
            else:
                llm_messages.append(AIMessage(content=message["content"]))
        try:
            response = await self.llm.ainvoke(llm_messages)
            return response.content.strip()
        except Exception as e:
            logger.error("LLM chat generation failed: %s", e)
            raise
