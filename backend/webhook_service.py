"""
Delivers HMAC-signed webhook notifications for register/verify events to
an org's configured webhook_url. Best-effort: failures are logged, never
raised into the request path (a slow/broken webhook endpoint should never
break registration or verification for the caller).
"""

import hashlib
import hmac
import json
import logging

import requests

from config import settings

logger = logging.getLogger("aqtify.webhooks")


def sign_payload(secret, payload_bytes):
    return hmac.new(secret.encode(), payload_bytes, hashlib.sha256).hexdigest()


def send_webhook(webhook_url, webhook_secret, event_type, data):
    if not webhook_url:
        return {"sent": False, "reason": "no webhook_url configured for this org"}

    payload = {"event": event_type, "data": data}
    payload_bytes = json.dumps(payload, default=str).encode()
    signature = sign_payload(webhook_secret or "", payload_bytes)

    headers = {
        "Content-Type": "application/json",
        "X-Aqtify-Signature": signature,
        "X-Aqtify-Event": event_type,
    }

    for attempt in range(settings.WEBHOOK_MAX_RETRIES + 1):
        try:
            resp = requests.post(
                webhook_url, data=payload_bytes, headers=headers,
                timeout=settings.WEBHOOK_TIMEOUT_SECONDS,
            )
            if resp.status_code < 400:
                return {"sent": True, "status_code": resp.status_code}
        except Exception as exc:
            logger.warning("Webhook delivery attempt %d to %s failed: %s", attempt + 1, webhook_url, exc)

    return {"sent": False, "reason": "all delivery attempts failed"}
