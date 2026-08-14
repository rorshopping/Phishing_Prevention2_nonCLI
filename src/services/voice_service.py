import asyncio
import logging
import uuid
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape as xml_escape

import httpx

from src.config import settings

logger = logging.getLogger(__name__)

TTS_DIR = Path(__file__).resolve().parent.parent.parent / "static" / "tts"


class VoiceService:
    def __init__(self) -> None:
        self.azure_key = settings.azure_speech_key
        self.azure_region = settings.azure_speech_region or "germanywestcentral"
        self.azure_voice = settings.azure_speech_voice or "de-DE-ConradNeural"
        self.base_url = (settings.app_base_url or "").rstrip("/")
        self.openai_key = settings.openai_api_key or settings.llm_api_key
        self.openai_base_url = "https://api.openai.com/v1"

    async def synthesize(self, text: str, voice: str | None = None) -> dict[str, Any]:
        if self.azure_key:
            return await self._synthesize_azure(text, voice)
        if self.openai_key:
            return await self._synthesize_openai(text, voice)
        raise RuntimeError("No TTS provider configured (set AZURE_SPEECH_KEY or OPENAI_API_KEY)")

    async def _synthesize_azure(self, text: str, voice: str | None) -> dict[str, Any]:
        if not self.base_url:
            raise RuntimeError("APP_BASE_URL not set; cannot expose TTS audio to Twilio")

        voice = voice or self.azure_voice
        language = voice.split("-Neural")[0]
        ssml = (
            '<speak version="1.0" xml:lang="%s" xmlns="http://www.w3.org/2001/10/synthesis">'
            '<voice name="%s">%s</voice></speak>'
        ) % (language, voice, xml_escape(text))

        url = f"https://{self.azure_region}.tts.speech.microsoft.com/cognitiveservices/v1"
        headers = {
            "Ocp-Apim-Subscription-Key": self.azure_key,
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": "audio-24khz-96kbitrate-mono-mp3",
            "User-Agent": "PhishGuard",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, headers=headers, content=ssml)
            resp.raise_for_status()

        filename = f"{uuid.uuid4().hex}.mp3"
        tts_dir = TTS_DIR
        tts_dir.mkdir(parents=True, exist_ok=True)
        await asyncio.to_thread((tts_dir / filename).write_bytes, resp.content)

        return {
            "url": f"{self.base_url}/tts/{filename}",
            "filename": filename,
            "format": "mp3",
            "content_length": len(resp.content),
            "provider": "azure",
            "voice": voice,
        }

    async def synthesize_pcm(self, text: str, voice: str | None = None) -> bytes:
        if not self.azure_key:
            raise RuntimeError("AZURE_SPEECH_KEY not set; cannot synthesize live audio")
        voice = voice or self.azure_voice
        return await asyncio.to_thread(self._synthesize_pcm_blocking, text, voice)

    def _synthesize_pcm_blocking(self, text: str, voice: str) -> bytes:
        from azure.cognitiveservices import speech as speechsdk

        speech_config = speechsdk.SpeechConfig(subscription=self.azure_key, region=self.azure_region)
        speech_config.speech_synthesis_voice_name = voice
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
        result = synthesizer.speak_text_async(text).get()
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            return result.audio_data or b""
        raise RuntimeError(f"Azure TTS failed: {result.reason}")

    async def _synthesize_openai(self, text: str, voice: str | None) -> dict[str, Any]:
        if not self.base_url:
            raise RuntimeError("APP_BASE_URL not set; cannot expose TTS audio to Twilio")

        voice = voice or "alloy"
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    f"{self.openai_base_url}/audio/speech",
                    headers={"Authorization": f"Bearer {self.openai_key}"},
                    json={
                        "model": "tts-1",
                        "input": text,
                        "voice": voice,
                        "response_format": "mp3",
                    },
                )
                resp.raise_for_status()
        except Exception as e:
            logger.error("OpenAI voice synthesis failed: %s", e)
            raise

        filename = f"{uuid.uuid4().hex}.mp3"
        tts_dir = TTS_DIR
        tts_dir.mkdir(parents=True, exist_ok=True)
        await asyncio.to_thread((tts_dir / filename).write_bytes, resp.content)

        return {
            "url": f"{self.base_url}/tts/{filename}",
            "filename": filename,
            "format": "mp3",
            "content_length": len(resp.content),
            "provider": "openai",
            "voice": voice,
        }
