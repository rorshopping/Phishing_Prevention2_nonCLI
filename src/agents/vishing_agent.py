import uuid
import logging
from datetime import datetime
from typing import Any
from xml.sax.saxutils import escape as xml_escape

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import async_session
from src.database.models import VishingSession, Employee, Campaign
from src.services.twilio_service import TwilioService
from src.services.voice_service import VoiceService
from src.engine.vishing_script_generator import VishingScriptGenerator
from src.agents.base import BaseAgent
from src.config import settings

logger = logging.getLogger(__name__)


VISHING_SCENARIOS = {
    "tech_support": "Posing as IT support needing password reset",
    "bank_fraud": "Posing as bank fraud department verifying a transaction",
    "hr_benefits": "Posing as HR with urgent benefits update",
    "vendor_call": "Posing as vendor requesting invoice payment",
    "ceo_urgence": "Posing as CEO requesting urgent wire transfer",
}

VISHING_DISCLOSE_KEY = "1"


class VishingAgent(BaseAgent):
    def __init__(
        self,
        twilio: TwilioService | None = None,
        voice: VoiceService | None = None,
        script_generator: VishingScriptGenerator | None = None,
    ) -> None:
        self.twilio = twilio or TwilioService()
        self.voice = voice or VoiceService()
        self.script_generator = script_generator or VishingScriptGenerator()

    async def trigger_vishing_call(
        self,
        employee_id: uuid.UUID,
        campaign_id: uuid.UUID | None = None,
        scenario: str = "tech_support",
    ) -> dict[str, Any]:
        async with async_session() as db:
            employee = await self._load_employee(db, employee_id)
            if not employee:
                return {"error": "Employee not found", "employee_id": str(employee_id)}

            campaign = None
            if campaign_id:
                campaign = await self._load_campaign(db, campaign_id)

            client_id = employee.client_id
            if campaign:
                client_id = campaign.client_id

            if not settings.twilio_account_sid or not settings.twilio_auth_token:
                logger.warning("Twilio not configured — simulating vishing call for employee %s", employee_id)
                return await self._simulate_call(db, employee, campaign, scenario, client_id)

            if settings.vishing_live and settings.app_base_url and settings.azure_speech_key:
                return await self._trigger_live_call(db, employee, campaign, scenario, client_id)

            try:
                script = await self._generate_script(employee, scenario)

                voice_url = await self._synthesize_script(script.get("text", ""))

                twiml = self._build_twiml(script, voice_url)

                session = VishingSession(
                    client_id=client_id,
                    employee_id=employee.id,
                    campaign_id=campaign.id if campaign else None,
                    status="in_progress",
                    ai_used=True,
                    transcript=script.get("text", ""),
                    twiml=twiml,
                )
                db.add(session)
                await db.flush()

                call_sid = await self._place_call(employee, twiml, session.id)
                session.twilio_sid = call_sid

                await self._log_action(
                    db,
                    client_id,
                    "vishing_call_triggered",
                    {
                        "session_id": str(session.id),
                        "employee_id": str(employee.id),
                        "scenario": scenario,
                        "twilio_sid": call_sid,
                    },
                )

                await db.commit()

                return {
                    "session_id": str(session.id),
                    "twilio_sid": call_sid,
                    "status": "in_progress",
                    "scenario": scenario,
                }

            except Exception:
                await db.rollback()
                logger.exception("Vishing call failed for employee %s", employee_id)

                session = VishingSession(
                    client_id=client_id,
                    employee_id=employee.id,
                    campaign_id=campaign.id if campaign else None,
                    status="failed",
                    ai_used=True,
                )
                db.add(session)
                await db.commit()

                return {
                    "error": "Vishing call failed",
                    "employee_id": str(employee_id),
                    "status": "failed",
                }

    async def record_outcome(self, session_id: uuid.UUID, disclosed: bool) -> dict[str, Any]:
        async with async_session() as db:
            result = await db.execute(
                select(VishingSession).where(VishingSession.id == session_id)
            )
            session = result.scalar_one_or_none()
            if not session:
                return {"error": "Session not found"}

            session.sensitive_info_disclosed = disclosed
            session.status = "completed"

            await self._log_action(
                db,
                session.client_id,
                "vishing_outcome_recorded",
                {
                    "session_id": str(session_id),
                    "sensitive_info_disclosed": disclosed,
                },
            )

            await db.commit()
            return {"session_id": str(session_id), "disclosed": disclosed}

    async def _load_employee(self, db: AsyncSession, employee_id: uuid.UUID) -> Employee | None:
        result = await db.execute(select(Employee).where(Employee.id == employee_id))
        return result.scalar_one_or_none()

    async def _load_campaign(self, db: AsyncSession, campaign_id: uuid.UUID) -> Campaign | None:
        result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
        return result.scalar_one_or_none()

    async def _generate_script(self, employee: Employee, scenario: str) -> dict[str, Any]:
        scenario_desc = VISHING_SCENARIOS.get(scenario, "General phishing simulation call")
        language = settings.language or "de"
        context = {
            "name": employee.name_hash or "valued employee",
            "role": employee.role or "team member",
            "department": employee.department or "our company",
            "scenario": scenario_desc,
            "language": language,
        }

        try:
            script = await self.script_generator.generate(context)
            return script
        except Exception:
            logger.warning("Script generation failed, using fallback")
            if language == "de":
                return {
                    "text": (
                        f"Hallo {context['name']}, hier ist {context['department']} IT-Sicherheit. "
                        f"Wir haben ungewöhnliche Aktivitäten auf Ihrem Konto festgestellt. "
                        f"Bitte verifizieren Sie Ihre Zugangsdaten, indem Sie die 1 auf Ihrer Tastatur drücken. "
                        f"Dies ist eine automatisierte Sicherheitsprüfung."
                    ),
                    "scenario": scenario,
                }
            return {
                "text": (
                    f"Hello {context['name']}, this is {context['department']} IT security. "
                    f"We've detected unusual activity on your account. "
                    f"Please verify your credentials by pressing 1 on your keypad. "
                    f"This is an automated security check."
                ),
                "scenario": scenario,
            }

    async def _synthesize_script(self, text: str) -> str | None:
        try:
            result = await self.voice.synthesize(text)
            return result.get("url") if isinstance(result, dict) else None
        except Exception:
            logger.warning("Voice synthesis failed, using Twilio TTS fallback")
            return None

    async def _place_call(self, employee: Employee, twiml: str, session_id: uuid.UUID | None = None) -> str:
        phone = employee.phone_number
        if not phone:
            logger.error("No phone number set for employee %s; cannot place call", employee.id)
            return ""

        url = None
        base = (settings.app_base_url or "").rstrip("/")
        if base and session_id:
            url = f"{base}/webhooks/vishing/twiml?session_id={session_id}"

        result = await self.twilio.make_call(
            to=phone,
            twiml=twiml,
            url=url,
        )
        return result.get("sid", "")

    async def _trigger_live_call(
        self,
        db: AsyncSession,
        employee: Employee,
        campaign: Campaign | None,
        scenario: str,
        client_id: uuid.UUID,
    ) -> dict[str, Any]:
        session = VishingSession(
            client_id=client_id,
            employee_id=employee.id,
            campaign_id=campaign.id if campaign else None,
            status="in_progress",
            ai_used=True,
        )
        db.add(session)
        await db.flush()

        wss = (
            settings.app_base_url.replace("https://", "wss://", 1).replace("http://", "ws://", 1)
        ).rstrip("/")
        stream_url = f"{wss}/vishing/ws/vishing/{session.id}"
        twiml = (
            '<Response><Connect><Stream url="{url}">'
            '<Parameter name="sessionId" value="{sid}"/>'
            '<Parameter name="scenario" value="{scenario}"/>'
            "</Stream></Connect></Response>"
        ).format(
            url=xml_escape(stream_url),
            sid=str(session.id),
            scenario=xml_escape(scenario),
        )
        session.twiml = twiml

        call_sid = await self._place_call(employee, twiml, session.id)
        session.twilio_sid = call_sid

        await self._log_action(
            db,
            client_id,
            "vishing_call_triggered",
            {
                "session_id": str(session.id),
                "employee_id": str(employee.id),
                "scenario": scenario,
                "twilio_sid": call_sid,
                "live": True,
            },
        )
        await db.commit()

        return {
            "session_id": str(session.id),
            "twilio_sid": call_sid,
            "status": "in_progress",
            "scenario": scenario,
            "live": True,
        }

    def _build_twiml(self, script: dict[str, Any], voice_url: str | None) -> str:
        if voice_url:
            content = f"<Play>{xml_escape(voice_url)}</Play>"
        else:
            content = (
                '<Say voice="Polly.Hans" language="de-DE">'
                f"{xml_escape(script.get('text', ''))}"
                "</Say>"
            )

        base = (settings.app_base_url or "").rstrip("/")
        if not base:
            logger.warning("APP_BASE_URL not set — no DTMF outcome capture for this call")
            return f"<Response>{content}</Response>"

        action = f"{base}/webhooks/vishing/gather"
        return (
            '<Response><Gather input="dtmf" numDigits="1" timeout="5" '
            f'action="{xml_escape(action)}" method="POST">'
            f"{content}"
            "</Gather></Response>"
        )

    async def _simulate_call(
        self,
        db: AsyncSession,
        employee: Employee,
        campaign: Campaign | None,
        scenario: str,
        client_id: uuid.UUID,
    ) -> dict[str, Any]:
        script = await self._generate_script(employee, scenario)

        session = VishingSession(
            client_id=client_id,
            employee_id=employee.id,
            campaign_id=campaign.id if campaign else None,
            status="simulated",
            ai_used=False,
            transcript=script.get("text", ""),
        )
        db.add(session)
        await db.flush()

        await self._log_action(
            db,
            client_id,
            "vishing_simulated",
            {
                "session_id": str(session.id),
                "employee_id": str(employee.id),
                "scenario": scenario,
            },
        )

        await db.commit()

        return {
            "session_id": str(session.id),
            "status": "simulated",
            "scenario": scenario,
            "note": "Twilio not configured — call was simulated",
        }


