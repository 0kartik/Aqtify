"""
Central configuration. Everything that's an external credential or a
deployment-specific value is read from the environment (via a local .env
file — see .env.example) so nothing sensitive is hardcoded or committed.

Every setting has a safe local-dev default/no-op, so the app runs with
zero configuration -- features that need a real credential (email,
webhooks, Postgres, Redis, Sentry, TLS) just quietly stay disabled until
you fill in `.env`.
"""

import os
from dotenv import load_dotenv

load_dotenv()


def _bool(env_var, default=False):
    val = os.getenv(env_var)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")


def _int(env_var, default):
    val = os.getenv(env_var)
    try:
        return int(val) if val is not None else default
    except ValueError:
        return default


class Settings:
    # -----------------------------------------------------------
    # Database -- defaults to local SQLite; set DATABASE_URL for Postgres
    # -----------------------------------------------------------
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///authenticity_registry.db")

    # -----------------------------------------------------------
    # Redis -- rate limiting + review-queue counters.
    # Falls back to an in-memory limiter (per-process only) if unset.
    # -----------------------------------------------------------
    REDIS_URL = os.getenv("REDIS_URL", "")  # e.g. redis://localhost:6379/0

    # -----------------------------------------------------------
    # Email (SMTP) -- used to send the secured file + certificate to the
    # owner after registration. Leave blank to disable (logs instead of sending).
    # -----------------------------------------------------------
    SMTP_HOST = os.getenv("SMTP_HOST", "")
    SMTP_PORT = _int("SMTP_PORT", 587)
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM = os.getenv("SMTP_FROM", "noreply@aqtify.example")
    SMTP_USE_TLS = _bool("SMTP_USE_TLS", True)

    # -----------------------------------------------------------
    # Webhooks -- outbound notifications on register/verify events.
    # Payloads are HMAC-SHA256 signed with each org's webhook secret
    # (auto-generated per org, rotatable via /api/webhooks/rotate-secret).
    # -----------------------------------------------------------
    WEBHOOK_TIMEOUT_SECONDS = _int("WEBHOOK_TIMEOUT_SECONDS", 5)
    WEBHOOK_MAX_RETRIES = _int("WEBHOOK_MAX_RETRIES", 2)

    # -----------------------------------------------------------
    # AI-detection gate (feature: block/flag AI-generated media at registration)
    # -----------------------------------------------------------
    AI_FLAG_THRESHOLD = _int("AQTIFY_AI_FLAG_THRESHOLD", 10)   # % -- above this: flagged for review, still registers
    AI_BLOCK_THRESHOLD = _int("AQTIFY_AI_BLOCK_THRESHOLD", 60)  # % -- above this: registration is rejected outright

    # -----------------------------------------------------------
    # Secrets / auth
    # -----------------------------------------------------------
    APP_SECRET_KEY = os.getenv("APP_SECRET_KEY", "")  # set a random 32+ char value in production

    # -----------------------------------------------------------
    # TLS -- only used if you run uvicorn directly with TLS instead of
    # terminating it at a reverse proxy (recommended). Leave blank to run
    # plain HTTP behind e.g. nginx/Caddy, which handle TLS instead.
    # -----------------------------------------------------------
    SSL_KEYFILE = os.getenv("SSL_KEYFILE", "")
    SSL_CERTFILE = os.getenv("SSL_CERTFILE", "")

    # -----------------------------------------------------------
    # Monitoring / logging
    # -----------------------------------------------------------
    SENTRY_DSN = os.getenv("SENTRY_DSN", "")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = os.getenv("LOG_FORMAT", "json")  # "json" or "text"

    # -----------------------------------------------------------
    # Public badge / embed widget
    # -----------------------------------------------------------
    PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://127.0.0.1:8000")


settings = Settings()
