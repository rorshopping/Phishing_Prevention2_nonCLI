import logging
from typing import Any

from src.services.llm_service import LLMService

logger = logging.getLogger(__name__)


class VishingScriptGenerator:
    def __init__(self, llm: LLMService | None = None) -> None:
        self.llm = llm or LLMService()

    async def generate(self, context: dict[str, Any]) -> dict[str, Any]:
        name = context.get("name", "valued employee")
        role = context.get("role", "team member")
        department = context.get("department", "our company")
        scenario = context.get("scenario", "General security check")

        prompt = (
            f"Generate a short vishing (voice phishing) call script for a security awareness test.\n\n"
            f"Context:\n"
            f"- Employee name: {name}\n"
            f"- Role: {role}\n"
            f"- Company department: {department}\n"
            f"- Scenario: {scenario}\n\n"
            f"Requirements:\n"
            f"- The script should be a natural, conversational phone call (max 150 words)\n"
            f"- The caller should sound official and create realistic urgency\n"
            f"- Include a prompt for the target to disclose credentials or sensitive info\n"
            f"- Do NOT include any disclaimers about it being a test\n"
            f"- Return ONLY the script text, no formatting or explanation"
        )

        try:
            text = await self.llm.generate(prompt)
            return {"text": text, "scenario": scenario}
        except Exception as e:
            logger.warning("Script generation failed, using fallback: %s", e)
            return self._fallback_script(context)

    def _fallback_script(self, context: dict[str, Any]) -> dict[str, Any]:
        name = context.get("name", "valued employee")
        scenario = context.get("scenario", "General")
        return {
            "text": (
                f"Hello {name}, this is IT security. We've detected unusual login activity "
                f"on your corporate account. To verify your identity, please provide your "
                f"username and the verification code sent to your phone. "
                f"This is urgent - your account may be locked otherwise. "
                f"Please call back at 030 1234567 and reference ticket SEC-{abs(hash(name)) % 100000}."
            ),
            "scenario": scenario,
        }
