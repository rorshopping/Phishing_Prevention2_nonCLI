import logging
import smtplib
from email.message import EmailMessage

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(tags=["contact"])


class ContactForm(BaseModel):
    company_name: str
    email: str
    employees: str
    interest: str
    message: str = ""


@router.post("/api/contact")
async def contact_submit(form: ContactForm):
    if not settings.gmail_user or not settings.gmail_app_password:
        logger.error("Gmail SMTP not configured")
        raise HTTPException(status_code=500, detail="Contact form not available")

    msg = EmailMessage()
    msg["Subject"] = f"New Contact: {form.company_name}"
    msg["From"] = settings.gmail_user
    msg["To"] = "rorshopping@gmail.com"

    body = f"""New Contact Form Submission

Company:  {form.company_name}
Email:    {form.email}
Employees: {form.employees}
Interest: {form.interest}
Message:  {form.message or "(none)"}
"""
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(settings.gmail_user, settings.gmail_app_password)
            smtp.send_message(msg)
        logger.info("Contact email sent from %s (%s)", form.email, form.company_name)
        return {"status": "ok", "message": "Message sent. We'll be in touch within 24 hours."}
    except Exception as exc:
        logger.exception("Failed to send contact email")
        raise HTTPException(status_code=502, detail="Failed to deliver message. Please email us directly at rorshopping@gmail.com.")
