"""
Structured logging setup. Set LOG_FORMAT=json in .env for JSON logs
(recommended in production, so a log aggregator can parse them), or
LOG_FORMAT=text for human-readable local dev output.

If SENTRY_DSN is set in .env, errors are also reported to Sentry
(requires `pip install sentry-sdk`, already in requirements.txt).
"""

import json
import logging
import sys
import time

from config import settings


class JsonFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(record.created)),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload)


def setup_logging():
    root = logging.getLogger()
    root.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

    handler = logging.StreamHandler(sys.stdout)
    if settings.LOG_FORMAT == "json":
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))

    root.handlers = [handler]

    if settings.SENTRY_DSN:
        try:
            import sentry_sdk
            sentry_sdk.init(dsn=settings.SENTRY_DSN, traces_sample_rate=0.1)
            logging.getLogger("aqtify").info("Sentry monitoring enabled")
        except ImportError:
            logging.getLogger("aqtify").warning("SENTRY_DSN set but sentry-sdk isn't installed")
