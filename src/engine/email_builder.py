import logging
import re
from enum import Enum
from typing import Any

from jinja2 import Environment, BaseLoader
from openai import AsyncOpenAI

from src.config import settings

logger = logging.getLogger(__name__)


class ScenarioType(str, Enum):
    bank_transfer = "bank_transfer"
    password_reset = "password_reset"
    invoice = "invoice"
    calendar_invite = "calendar_invite"
    voicemail = "voicemail"
    shared_doc = "shared_doc"
    security_alert = "security_alert"
    bonus = "bonus"
    vacation_policy = "vacation_policy"
    urgent_review = "urgent_review"


PLANNER_TO_EMAIL_SCENARIO: dict[str, ScenarioType] = {
    "credential_harvest": ScenarioType.password_reset,
    "malware_attachment": ScenarioType.shared_doc,
    "urgency_alert": ScenarioType.urgent_review,
    "ceo_fraud": ScenarioType.bank_transfer,
    "invoice_fraud": ScenarioType.invoice,
    "cloud_notification": ScenarioType.security_alert,
    "calendar_invite": ScenarioType.calendar_invite,
    "voicemail_phish": ScenarioType.voicemail,
    "dropbox_share": ScenarioType.shared_doc,
    "linkedin_message": ScenarioType.shared_doc,
}


SCENARIO_PROMPTS: dict[ScenarioType, str] = {
    ScenarioType.bank_transfer: (
        "Dringende Zahlungsbenachrichtigung der Finanzabteilung, die die sofortige Genehmigung "
        "einer verdächtigen Überweisung erfordert. Erzeuge ein Gefühl von Dringlichkeit und Autorität."
    ),
    ScenarioType.password_reset: (
        "Passwortablauf-Benachrichtigung, die den Mitarbeiter auffordert, sein Konto durch Klicken "
        "eines Links zu verifizieren. Imitiere eine IT-Sicherheitsbenachrichtigung."
    ),
    ScenarioType.invoice: (
        "Überfällige Rechnung eines bekannten Lieferanten mit einem Anhang-Link. Der Mitarbeiter "
        "wird aufgefordert, die Zahlung zu prüfen und freizugeben."
    ),
    ScenarioType.calendar_invite: (
        "Kalendereinladung für ein Meeting mit einer Führungskraft. Die Einladung enthält einen "
        "Link zur Bestätigung der Teilnahme, der zu einer Anmeldeseite führt."
    ),
    ScenarioType.voicemail: (
        "Sprachnachrichten-Benachrichtigung mit einem Link zum Abspielen der Nachricht. Gib vor, "
        "vom Telefonsystem des Unternehmens zu sein."
    ),
    ScenarioType.shared_doc: (
        "Dokumentfreigabe-Benachrichtigung von einem Kollegen (z.B. Google Docs / Office 365). "
        "Der Link erfordert eine Anmeldung zum Anzeigen."
    ),
    ScenarioType.security_alert: (
        "Sicherheitswarnung über einen verdächtigen Anmeldeversuch auf dem Konto des Mitarbeiters. "
        "Fordere zur sofortigen Überprüfung der Aktivität auf."
    ),
    ScenarioType.bonus: (
        "Jahresendprämie oder Gehaltsupdate-Benachrichtigung. Der Mitarbeiter muss sich anmelden, "
        "um die Bonusdetails einzusehen."
    ),
    ScenarioType.vacation_policy: (
        "Aktualisierte Urlaubsrichtlinie, die die Bestätigung des Mitarbeiters erfordert. Der Link "
        "führt zu einer Anmeldeseite, die als HR-Portal getarnt ist."
    ),
    ScenarioType.urgent_review: (
        "Dringende Dokumentenprüfungsanfrage eines Managers. Das Dokument ist als vertraulich "
        "markiert und erfordert sofortige Aufmerksamkeit."
    ),
}


_EMAIL_TEMPLATE = """\
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
{{ body }}
</body>
</html>
"""

_jinja_env = Environment(loader=BaseLoader(), autoescape=False)


def _render_html(body_html_fragment: str) -> str:
    tpl = _jinja_env.from_string(_EMAIL_TEMPLATE)
    return tpl.render(body=body_html_fragment)


def _clean_subject(subject: str) -> str:
    subject = subject.replace("\u2013", "-").replace("\u2014", "--")
    subject = subject.replace("\u2018", "'").replace("\u2019", "'")
    subject = subject.replace("\u201c", '"').replace("\u201d", '"')
    subject = subject.replace("\u2026", "...")
    return subject


def _build_llm(
    model: str = "",
    api_key: str = "",
    base_url: str = "",
) -> AsyncOpenAI:
    return AsyncOpenAI(
        api_key=api_key or settings.llm_api_key,
        base_url=base_url or settings.llm_base_url,
        timeout=60.0,
        max_retries=0,  # _try_provider does its own 2-attempt loop
    )


async def _try_provider(
    system: str,
    user: str,
    label: str,
    model: str = "",
    api_key: str = "",
    base_url: str = "",
) -> str:
    llm = _build_llm(model=model, api_key=api_key, base_url=base_url)
    for attempt in range(2):
        try:
            response = await llm.chat.completions.create(
                model=model or settings.llm_model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=0.9,
                max_tokens=1024,
            )
            raw = (response.choices[0].message.content or "").strip()
            if raw:
                return raw
            logger.warning("%s empty response on attempt %d/2", label, attempt + 1)
        except Exception as e:
            logger.warning("%s call failed on attempt %d/2: %s", label, attempt + 1, e)
    return ""


def _build_system_prompt() -> str:
    return (
        "You are a phishing simulation email generator. Generate realistic, context-aware "
        "phishing email content for security awareness training. "
        "ALL emails MUST be written in German language. "
        "Return ONLY valid JSON with keys: subject, body_html. "
        "The body_html must be HTML fragment (no <html>/<body> tags). "
        "Do NOT include any markdown formatting or explanation. "
        "CRITICAL: Use '{{.URL}}' as the placeholder for ALL links "
        "(do NOT use any real or made-up URLs). "
        "CRITICAL: Use '{{.FirstName}}' for the recipient's first name "
        "(do NOT use any real name). "
        "CRITICAL: Do NOT include any disclosure, disclaimer, or training notice. "
        "The email must appear as a genuine real-world message with no indication "
        "it is a simulation or security test."
    )


def _build_user_prompt(
    scenario_type: ScenarioType,
    employee_context: dict[str, Any],
    company_context: dict[str, Any],
) -> str:
    scenario_desc = SCENARIO_PROMPTS[scenario_type]
    employee_name = employee_context.get("name", "Employee")
    role = employee_context.get("role", "employee")
    company = company_context.get("name", "the company")
    industry = company_context.get("industry", "")

    return (
        f"Scenario: {scenario_type.value}\n"
        f"Description: {scenario_desc}\n"
        f"Employee: {employee_name}, role: {role}\n"
        f"Company: {company} ({industry})\n"
        f"Generate a short phishing email in German language (max 200 words) that references the "
        f"employee's role and company context naturally."
    )


async def generate_email(
    scenario_type: ScenarioType,
    employee_context: dict[str, Any],
    company_context: dict[str, Any],
) -> dict[str, str]:
    system = _build_system_prompt()
    user = _build_user_prompt(scenario_type, employee_context, company_context)

    raw = await _try_provider(system, user, "OpenRouter")

    if not raw and settings.fallback_llm_api_key:
        logger.warning("OpenRouter failed, trying Groq fallback")
        raw = await _try_provider(
            system, user, "Groq",
            model=settings.fallback_llm_model,
            api_key=settings.fallback_llm_api_key,
            base_url=settings.fallback_llm_base_url,
        )

    try:
        if not raw:
            logger.warning("All LLM providers exhausted")
            raise ValueError("Empty LLM response")

        logger.debug("LLM raw response (first 500 chars): %s", raw[:500])

        if raw.startswith("```"):
            raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

        import json

        result: dict[str, str] = json.loads(raw)
        result["subject"] = _clean_subject(result.get("subject", ""))
        body = result.get("body_html", "")
        body = re.sub(r'https?://[^\s"\'<>]+', "{{.URL}}", body)
        result["body_html"] = _render_html(body)
        return result
    except Exception as e:
        logger.warning("LLM email generation failed, using fallback: %s", e)
        return _fallback_email(scenario_type, employee_context, company_context)


def _fallback_email(
    scenario_type: ScenarioType,
    employee_context: dict[str, Any],
    company_context: dict[str, Any],
) -> dict[str, str]:
    name = employee_context.get("name", "Employee")
    company = company_context.get("name", "Your Company")

    fallbacks: dict[ScenarioType, tuple[str, str]] = {
        ScenarioType.bank_transfer: (
            f"Dringend: Überweisung freigeben",
            f"<p>Hallo {{{{.FirstName}}}},</p><p>Eine dringende Überweisung erfordert Ihre Freigabe "
            f"bis heute Ende des Tages. <a href='{{{{.URL}}}}'>Hier prüfen und freigeben</a>.</p>"
            f"<p>Finanzabteilung, {company}</p>",
        ),
        ScenarioType.password_reset: (
            f"Ihr Passwort läuft in 24 Stunden ab",
            f"<p>Hallo {{{{.FirstName}}}},</p><p>Ihr {company}-Passwort läuft bald ab. "
            f"<a href='{{{{.URL}}}}'>Konto verifizieren</a> um den Zugriff zu behalten.</p>"
            f"<p>IT-Sicherheitsteam</p>",
        ),
        ScenarioType.invoice: (
            f"Überfällige Rechnung #INV-2024-{hash(name) % 10000:04d}",
            f"<p>Hallo {{{{.FirstName}}}},</p><p>Eine offene Rechnung erfordert Ihre Prüfung. "
            f"<a href='{{{{.URL}}}}'>Rechnungsdetails ansehen</a> und Zahlung freigeben.</p>"
            f"<p>Kreditorenbuchhaltung, {company}</p>",
        ),
        ScenarioType.calendar_invite: (
            f"Einladung: Quartalsbesprechung",
            f"<p>Hallo {{{{.FirstName}}}},</p><p>Sie wurden zu einem Meeting eingeladen. "
            f"<a href='{{{{.URL}}}}'>Teilnahme bestätigen</a>.</p>"
            f"<p>Geschäftsleitung, {company}</p>",
        ),
        ScenarioType.voicemail: (
            f"Neue Sprachnachricht von +49 30 1234567",
            f"<p>Hallo {{{{.FirstName}}}},</p><p>Sie haben eine neue Sprachnachricht. "
            f"<a href='{{{{.URL}}}}'>Hier anhören</a>.</p>"
            f"<p>Telefonsystem {company}</p>",
        ),
        ScenarioType.shared_doc: (
            f"{{{{.FirstName}}}} – Dokument für Sie freigegeben",
            f"<p>Hallo {{{{.FirstName}}}},</p><p>Ein Kollege hat ein Dokument mit Ihnen geteilt. "
            f"<a href='{{{{.URL}}}}'>Im Browser öffnen</a>.</p>"
            f"<p>Dokumentenfreigabe, {company}</p>",
        ),
        ScenarioType.security_alert: (
            f"⚠ Neue Anmeldung von unbekanntem Gerät",
            f"<p>Hallo {{{{.FirstName}}}},</p><p>Wir haben eine neue Anmeldung an Ihrem "
            f"{company}-Konto von einem unbekannten Gerät festgestellt. "
            f"<a href='{{{{.URL}}}}'>Aktivität prüfen</a> falls das nicht Sie waren.</p>"
            f"<p>Sicherheitsteam, {company}</p>",
        ),
        ScenarioType.bonus: (
            f"Jahresendprämie – Informationen",
            f"<p>Hallo {{{{.FirstName}}}},</p><p>Ihre Jahresendprämie steht zur Ansicht bereit. "
            f"<a href='{{{{.URL}}}}'>Anmelden für Details</a>.</p>"
            f"<p>Personalabteilung, {company}</p>",
        ),
        ScenarioType.vacation_policy: (
            f"Aktualisierte Urlaubsrichtlinie – Handlung erforderlich",
            f"<p>Hallo {{{{.FirstName}}}},</p><p>{company} hat die Urlaubsrichtlinie aktualisiert. "
            f"<a href='{{{{.URL}}}}'>Prüfen und bestätigen</a> bis Ende der Woche.</p>"
            f"<p>Personalabteilung</p>",
        ),
        ScenarioType.urgent_review: (
            f"DRINGEND: Dokumentenprüfung angefordert",
            f"<p>Hallo {{{{.FirstName}}}},</p><p>Bitte prüfen Sie das beigefügte vertrauliche "
            f"Dokument dringend. <a href='{{{{.URL}}}}'>Sicheres Dokument öffnen</a>.</p>"
            f"<p>Management, {company}</p>",
        ),
    }

    subject, body_fragment = fallbacks.get(
        scenario_type,
        (f"Notification from {company}", f"<p>Hi {{{{.FirstName}}}},</p><p>Please <a href='{{{{.URL}}}}'>click here</a>.</p>"),
    )
    return {"subject": subject, "body_html": _render_html(body_fragment)}
