import logging

from pydantic_settings import BaseSettings
from pydantic import Field

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    database_url: str = Field(default="sqlite+aiosqlite:///./phishguard.db", description="Database connection string")
    gophish_api_url: str = Field(default="http://localhost:3333/api")
    gophish_api_key: str = Field(default="", min_length=1)
    llm_api_key: str = Field(default="", min_length=1)
    llm_model: str = "gpt-4o-mini"
    llm_base_url: str = "https://api.openai.com/v1"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "eu-central-1"
    email_source: str = "simulation@yourdomain.com"
    gmail_user: str = ""
    gmail_app_password: str = ""
    gmail_from: str = ""
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""
    serpapi_api_key: str = ""
    gdpr_hash_salt: str = Field(default="", min_length=16, description="Secret salt for PII hashing (min 16 chars)")
    log_level: str = "INFO"
    language: str = "de"
    app_secret_key: str = Field(default="", description="Secret for webhook HMAC validation")
    scheduler_interval_seconds: int = Field(default=300, ge=30, description="Background scheduler loop interval")
    gophish_phishing_server_url: str = Field(default="http://localhost:8080", description="Phishing server URL for Gophish campaign links")
    openai_api_key: str = Field(default="", description="Separate OpenAI API key for TTS (falls back to LLM_API_KEY)")
    alert_webhook_url: str = Field(default="", description="Webhook URL for campaign completion alerts (Slack, Teams, etc.)")
    alert_webhook_threshold: int = Field(default=0, ge=0, description="Minimum click count to trigger webhook alert (0 = always)")

    fallback_llm_api_key: str = ""
    fallback_llm_base_url: str = "https://api.groq.com/openai/v1"
    fallback_llm_model: str = "llama-3.3-70b-versatile"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    def validate_required(self) -> list[str]:
        missing = []
        if not self.gophish_api_key:
            missing.append("GOPHISH_API_KEY")
        if not self.llm_api_key:
            missing.append("LLM_API_KEY")
        if not self.gdpr_hash_salt:
            missing.append("GDPR_HASH_SALT (or APP_SECRET_KEY)")
        return missing


settings = Settings()
missing = settings.validate_required()
if missing:
    logger.warning("Missing required config: %s", ", ".join(missing))
