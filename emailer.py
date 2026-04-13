from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage


def _env_flag(name: str, default: str = "true") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


def email_configured() -> bool:
    required = ["SMTP_HOST", "SMTP_PORT", "SMTP_FROM_EMAIL"]
    return all(os.getenv(key) for key in required)


def send_email_message(to_email: str, subject: str, text_body: str, html_body: str | None = None) -> None:
    if not email_configured():
        raise RuntimeError("SMTP is not configured.")

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = os.getenv("SMTP_FROM_EMAIL", "")
    message["To"] = to_email
    message.set_content(text_body)
    if html_body:
        message.add_alternative(html_body, subtype="html")

    host = os.getenv("SMTP_HOST", "")
    port = int(os.getenv("SMTP_PORT", "587"))
    username = os.getenv("SMTP_USERNAME", "")
    password = os.getenv("SMTP_PASSWORD", "")
    use_tls = _env_flag("SMTP_USE_TLS", "true")

    with smtplib.SMTP(host, port, timeout=20) as server:
        server.ehlo()
        if use_tls:
            server.starttls()
            server.ehlo()
        if username:
            server.login(username, password)
        server.send_message(message)
