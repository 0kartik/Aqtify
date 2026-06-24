"""
Sends the secured (watermarked) file and certificate summary to the
media owner's email after registration. If SMTP isn't configured in
.env, this silently logs what it *would* have sent instead of failing
the registration -- email is a nice-to-have, not a blocker.
"""

import logging
import smtplib
from email.message import EmailMessage

from config import settings

logger = logging.getLogger("aqtify.email")


def is_configured():
    return bool(settings.SMTP_HOST and settings.SMTP_USER)


def send_registration_email(to_email, certificate_id, file_name, secured_file_path, media_type):
    if not to_email:
        return {"sent": False, "reason": "no owner_email provided"}

    if not is_configured():
        logger.info(
            "SMTP not configured -- would have emailed %s the certificate %s for %s",
            to_email, certificate_id, file_name,
        )
        return {"sent": False, "reason": "SMTP not configured (see .env.example)"}

    try:
        msg = EmailMessage()
        msg["Subject"] = f"Aqtify certificate {certificate_id} — {file_name}"
        msg["From"] = settings.SMTP_FROM
        msg["To"] = to_email
        msg.set_content(
            f"Your media has been registered with Aqtify.\n\n"
            f"Certificate ID: {certificate_id}\n"
            f"File: {file_name}\n"
            f"Media type: {media_type}\n\n"
            f"The secured (watermarked) file is attached. Keep it -- it's the "
            f"canonical artifact that will verify as AUTHENTIC.\n"
        )

        if secured_file_path:
            with open(secured_file_path, "rb") as f:
                data = f.read()
            subtype = "png" if secured_file_path.endswith(".png") else "octet-stream"
            maintype = "image" if subtype == "png" else "application"
            msg.add_attachment(data, maintype=maintype, subtype=subtype,
                                filename=secured_file_path.split("/")[-1])

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
            if settings.SMTP_USE_TLS:
                server.starttls()
            if settings.SMTP_USER:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)

        return {"sent": True}
    except Exception as exc:
        logger.warning("Failed to send registration email to %s: %s", to_email, exc)
        return {"sent": False, "reason": str(exc)}
