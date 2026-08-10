import asyncio
import base64
import logging
import uuid
from typing import Any

from src.config import settings
from src.database.models import VishingSession
from src.database.session import async_session
from src.services.llm_service import LLMService
from src.services.twilio_service import TwilioService
from src.services.voice_service import VoiceService
from src.agents.vishing_agent import VISHING_SCENARIOS
from src.utils.g711 import mulaw_to_pcm16k, pcm16k_to_mulaw

logger = logging.getLogger(__name__)

DISCLOSURE_PATTERNS = (
    "passwort",
    "kennwort",
    "benutzername",
    "benutzerkennung",
    "pin",
    "tan",
    "verifikationscode",
    "sicherheitscode",
    "zugangsdaten",
    "kreditkarten",
)

_PERSONA_SYSTEM = (
    "Du bist ein Test-Anrufer für eine interne Phishing-Sicherheitsübung (Vishing) eines "
    "deutschen Unternehmens. Dein Szenario: {scenario}. "
    "Du klingst offiziell und erzeugst realistische Dringlichkeit. "
    "Antworte natürlich und kurz (maximal 1-2 Sätze). "
    "Frage gezielt nach sensiblen Daten wie Passwort, Benutzername oder Bestätigungscode. "
    "Du darfst NIEMALS erwähnen, dass dies ein Test oder eine Übung ist. "
    "Bleibe bis zum Ende deiner Rolle. Antworte auf Deutsch."
)


class LiveVishingCaller:
    def __init__(self, session_id: str, language: str = "de") -> None:
        self.session_id = session_id
        self.language = language
        self.stream_sid: str | None = None
        self.call_sid: str | None = None
        self.scenario_desc: str = "Technischer Support ruft wegen verdächtiger Aktivität an."
        self._ws: Any = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._queue: asyncio.Queue = asyncio.Queue()
        self._history: list[dict[str, str]] = []
        self._busy = asyncio.Lock()
        self._push_stream: Any = None
        self._recognizer: Any = None
        self._llm = LLMService()
        self._voice = VoiceService()
        self._twilio = TwilioService()
        self._transcript: list[str] = []
        self.disclosed = False

    async def run(self, websocket: Any) -> None:
        self._ws = websocket
        self._loop = asyncio.get_running_loop()
        conversation_task: asyncio.Task | None = None
        try:
            await self._start_recognizer()
            conversation_task = asyncio.create_task(self._conversation_loop())

            while True:
                msg = await websocket.receive_json()
                event = msg.get("event")
                if event == "start":
                    self.call_sid = msg["start"].get("callSid")
                    self.stream_sid = msg["start"].get("streamSid")
                    params = msg["start"].get("customParameters") or {}
                    scenario = params.get("scenario", "tech_support")
                    self.scenario_desc = VISHING_SCENARIOS.get(
                        scenario, "Allgemeiner Sicherheits-Check"
                    )
                    await websocket.send_json(
                        {"event": "connected", "streamSid": self.stream_sid, "media": {"track": "outbound"}}
                    )
                    await self._handle_employee("")
                elif event == "media":
                    payload = msg["media"]["payload"]
                    if self._push_stream is not None:
                        self._push_stream.write(mulaw_to_pcm16k(base64.b64decode(payload)))
                elif event == "stop":
                    break
        except Exception:
            logger.exception("Live vishing stream error (session %s)", self.session_id)
        finally:
            if conversation_task is not None:
                conversation_task.cancel()
                try:
                    await conversation_task
                except asyncio.CancelledError:
                    pass
            await self._stop_recognizer()
            await self._finalize()

    async def _conversation_loop(self) -> None:
        while True:
            role, text = await self._queue.get()
            if role == "recognized" and text.strip():
                await self._handle_employee(text)

    async def _handle_employee(self, text: str) -> None:
        async with self._busy:
            if text:
                self._transcript.append(f"Mitarbeiter: {text}")
                if self._check_disclosure(text):
                    self.disclosed = True
                    await self._mark_disclosed()
                    text = f"{text} [Der Mitarbeiter hat soeben vertrauliche Daten preisgegeben.]"
                self._history.append({"role": "user", "content": text})
            else:
                self._history.append(
                    {"role": "user", "content": "(Das Gespräch beginnt – der Mitarbeiter hat abgehoben.)"}
                )

            reply = await self._get_reply()
            if not reply:
                return
            self._transcript.append(f"Anrufer: {reply}")
            self._history.append({"role": "assistant", "content": reply})
            await self._speak(reply)

            if self.disclosed:
                await asyncio.sleep(1.0)
                await self._hangup()

    async def _get_reply(self) -> str:
        system = _PERSONA_SYSTEM.format(scenario=self.scenario_desc)
        try:
            return await self._llm.chat(system, self._history[-10:])
        except Exception:
            logger.exception("LLM reply failed for vishing session %s", self.session_id)
            return ""

    def _check_disclosure(self, text: str) -> bool:
        lowered = text.lower()
        return any(pattern in lowered for pattern in DISCLOSURE_PATTERNS)

    async def _speak(self, text: str) -> None:
        if not self.stream_sid:
            return
        try:
            pcm = await self._voice.synthesize_pcm(text)
        except Exception:
            logger.exception("Live TTS failed for session %s", self.session_id)
            return
        if not pcm:
            return

        data = pcm16k_to_mulaw(pcm)
        for offset in range(0, len(data), 160):
            chunk = data[offset:offset + 160]
            await self._ws.send_json(
                {
                    "event": "media",
                    "streamSid": self.stream_sid,
                    "media": {"payload": base64.b64encode(chunk).decode()},
                }
            )

    async def _mark_disclosed(self) -> None:
        try:
            async with async_session() as db:
                session = await db.get(VishingSession, uuid.UUID(self.session_id))
                if session:
                    session.sensitive_info_disclosed = True
                    await db.commit()
        except Exception:
            logger.exception("Failed to mark vishing session %s as disclosed", self.session_id)

    async def _hangup(self) -> None:
        if self.call_sid:
            try:
                await self._twilio.hang_up(self.call_sid)
            except Exception:
                logger.exception("Failed to end call %s", self.call_sid)

    async def _start_recognizer(self) -> None:
        from azure.cognitiveservices import speech as speechsdk
        from azure.cognitiveservices.speech import audio as speech_audio

        speech_config = speechsdk.SpeechConfig(
            subscription=settings.azure_speech_key, region=settings.azure_speech_region
        )
        speech_config.speech_recognition_language = "de-DE"
        stream_format = speech_audio.AudioStreamFormat(
            samples_per_second=16000, bits_per_sample=16, channels=1
        )
        self._push_stream = speech_audio.PushAudioInputStream(stream_format)
        audio_config = speech_audio.AudioConfig(stream=self._push_stream)
        self._recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config, audio_config=audio_config
        )
        self._recognizer.recognized.connect(self._on_recognized)
        self._recognizer.start_continuous_recognition()

    def _on_recognized(self, evt: Any) -> None:
        from azure.cognitiveservices import speech as speechsdk

        result = getattr(evt, "result", None)
        text = getattr(result, "text", "") or ""
        if result and result.reason == speechsdk.ResultReason.RecognizedSpeech and text.strip():
            loop = self._loop
            if loop is not None:
                loop.call_soon_threadsafe(self._queue.put_nowait, ("recognized", text))

    async def _stop_recognizer(self) -> None:
        if self._recognizer is not None:
            try:
                self._recognizer.stop_continuous_recognition()
            except Exception:
                pass
        if self._push_stream is not None:
            try:
                self._push_stream.close()
            except Exception:
                pass

    async def _finalize(self) -> None:
        try:
            async with async_session() as db:
                session = await db.get(VishingSession, uuid.UUID(self.session_id))
                if session:
                    session.transcript = "\n".join(self._transcript)
                    session.sensitive_info_disclosed = self.disclosed
                    session.status = "completed"
                    await db.commit()
        except Exception:
            logger.exception("Failed to finalize vishing session %s", self.session_id)
