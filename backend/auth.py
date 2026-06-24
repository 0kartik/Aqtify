"""
API key issuance/verification, org RBAC checks, and rate limiting.

Rate limiting uses Redis (sliding window counter) if REDIS_URL is set in
.env, so limits are shared correctly across multiple server instances.
With no REDIS_URL, it falls back to an in-memory limiter that only works
correctly for a single process -- fine for local dev, not for a
multi-instance production deployment (this is exactly the gap the Redis
setting closes; see config.py / .env.example).
"""

import hashlib
import secrets
import time
from collections import defaultdict, deque

from fastapi import Header, HTTPException

from config import settings
from database import DatabaseManager

RATE_LIMIT_WINDOW_SECONDS = 60
RATE_LIMIT_MAX_REQUESTS = 60

# ---- in-memory fallback (single-process only) ----
_request_log = defaultdict(deque)

# ---- Redis client (only created if REDIS_URL is set) ----
_redis_client = None
if settings.REDIS_URL:
    try:
        import redis
        _redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        _redis_client.ping()
    except Exception:
        _redis_client = None  # fall back silently to in-memory


def _hash_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode()).hexdigest()


def generate_api_key(db: DatabaseManager, user_name=None, user_email=None,
                      key_mode="server", public_key_b64=None, org_id=None, role="owner"):
    """Create a new API key. Returns the raw key (shown once) + its id."""

    key_id = "key_" + secrets.token_hex(6)
    raw_key = "aqt_" + secrets.token_urlsafe(32)
    key_hash = _hash_key(raw_key)

    db.add_api_key(
        key_id=key_id, key_hash=key_hash, user_name=user_name, user_email=user_email,
        public_key=public_key_b64, key_mode=key_mode, org_id=org_id, role=role,
    )

    return {"key_id": key_id, "api_key": raw_key, "key_mode": key_mode, "org_id": org_id, "role": role}


def check_rate_limit(key_id: str):
    if _redis_client:
        redis_key = f"aqtify:ratelimit:{key_id}"
        try:
            count = _redis_client.incr(redis_key)
            if count == 1:
                _redis_client.expire(redis_key, RATE_LIMIT_WINDOW_SECONDS)
            if count > RATE_LIMIT_MAX_REQUESTS:
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded: {RATE_LIMIT_MAX_REQUESTS} requests per {RATE_LIMIT_WINDOW_SECONDS}s.",
                )
            return
        except HTTPException:
            raise
        except Exception:
            pass  # Redis hiccup -- fall through to in-memory so requests aren't blocked

    now = time.time()
    log = _request_log[key_id]
    while log and now - log[0] > RATE_LIMIT_WINDOW_SECONDS:
        log.popleft()
    if len(log) >= RATE_LIMIT_MAX_REQUESTS:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded: {RATE_LIMIT_MAX_REQUESTS} requests per {RATE_LIMIT_WINDOW_SECONDS}s.",
        )
    log.append(now)


def require_api_key(db: DatabaseManager):
    """Returns a FastAPI dependency bound to a given DatabaseManager instance."""

    def _dependency(x_api_key: str = Header(None)):
        if not x_api_key:
            raise HTTPException(status_code=401, detail="Missing X-API-Key header.")

        if not x_api_key.startswith("aqt_"):
            raise HTTPException(status_code=401, detail="Invalid API key.")

        record = db.get_api_key_by_hash(_hash_key(x_api_key))
        if record is None:
            raise HTTPException(status_code=401, detail="Invalid API key.")
        if record["revoked"]:
            raise HTTPException(status_code=401, detail="API key revoked.")

        check_rate_limit(record["key_id"])
        return record

    return _dependency


# -----------------------------------------------------------
# Org RBAC
# -----------------------------------------------------------
ROLE_RANK = {"viewer": 0, "member": 1, "admin": 2, "owner": 3}


def require_org_role(min_role: str):
    """FastAPI dependency factory: require the caller's org role to be
    at least `min_role` (owner > admin > member > viewer)."""

    def _dependency(key: dict):
        if not key.get("org_id"):
            raise HTTPException(status_code=403, detail="This action requires an organization account.")
        caller_rank = ROLE_RANK.get(key.get("role", "member"), 0)
        if caller_rank < ROLE_RANK[min_role]:
            raise HTTPException(status_code=403, detail=f"Requires '{min_role}' role or higher.")
        return key

    return _dependency


def new_webhook_secret():
    return secrets.token_hex(24)
