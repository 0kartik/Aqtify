# Aqtify — PQ-SMAP

**Post-Quantum Secure Media Authentication Protocol.**
Cryptographically sign, watermark, and verify images/audio/video using a
NIST post-quantum signature algorithm, with an AI-detection gate on
registration, email delivery, webhooks, bulk registration, org/team
accounts with RBAC, a public verification badge, and production-hardening
(Postgres/Redis, structured logging, secrets management).

---

## The 10 features in this build

1. **AI-detection gate on registration** — every image is screened before it's allowed to register. Below `AQTIFY_AI_FLAG_THRESHOLD` (default 10%): registers clean. Above it but below `AQTIFY_AI_BLOCK_THRESHOLD` (default 60%): registers but is queued in the review queue. Above the block threshold: registration is refused outright. Both thresholds are configurable in `.env`.
2. **Configurable threshold + review queue** — `/api/review-queue` lists flagged registrations; `/api/review-queue/{cert}/resolve` approves or rejects them. Also in the frontend's "Review Queue" tab.
3. **Email delivery** — if `owner_email` is given and SMTP is configured, the secured file + certificate are emailed automatically after registration (`send_email=false` to opt out per-call).
4. **Webhooks** — org-level `media.registered` / `media.verified` events, HMAC-SHA256 signed, POSTed to the org's configured `webhook_url` with retries. Best-effort — never blocks or fails the request that triggered them.
5. **Bulk/batch registration** — `POST /api/register/bulk` takes up to 50 files in one call; each gets its own AI gate + certificate; one bad file doesn't abort the batch.
6. **Org/team accounts with RBAC** — `/api/orgs` creates an organization; members have `viewer < member < admin < owner` roles enforced on org-scoped actions (managing members, setting the webhook, viewing all org records).
7. **Public verification badge widget** — `GET /api/badge/{certificate_id}.svg` (no auth) returns an embeddable shields.io-style badge; `GET /embed/{certificate_id}` returns a small standalone HTML page with embed instructions.
8. **PostgreSQL + Redis** — `database.py` runs on SQLAlchemy Core, so the exact same code works against local SQLite (zero-config default) or Postgres (`DATABASE_URL` in `.env`). Rate limiting uses Redis if `REDIS_URL` is set (correct across multiple instances), else an in-memory fallback (single-instance only).
9. **TLS + secrets management** — every credential (SMTP, DB, Redis, webhook config, Sentry, app secret, TLS cert paths) lives in one `.env` file (see `.env.example`), loaded via `python-dotenv`. Nothing is hardcoded. TLS is meant to be terminated at a reverse proxy (nginx/Caddy) in production; `SSL_KEYFILE`/`SSL_CERTFILE` are there if you want uvicorn to terminate it directly instead.
10. **Structured logging & monitoring** — JSON-formatted logs (`LOG_FORMAT=json`) for log aggregators, a `/health` endpoint that checks DB connectivity, and optional Sentry error reporting (`SENTRY_DSN`).

**On top of the earlier session's work:** ML-DSA-65 post-quantum signatures, image/audio/video watermarking + fingerprinting, per-user non-custodial keypairs, chain-of-custody logging, a C2PA-inspired manifest export, and a Manifest V3 browser extension. See git history / prior sections of this README for how those work — this file documents the current end state.

---

## ⚠️ Where to put your keys

Every external credential this project can use lives in **`backend/.env`**
(copy from `backend/.env.example`). Nothing is hardcoded anywhere else.
Everything is optional — the app runs with zero configuration using
SQLite + in-memory rate limiting + no-op email/webhooks/monitoring; fill
in a section to turn that feature on.

```bash
cd backend
cp .env.example .env
```

```ini
# backend/.env

# ---- Database (Postgres) ----
# DATABASE_URL=postgresql://user:password@localhost:5432/aqtify

# ---- Redis (rate limiting) ----
# REDIS_URL=redis://localhost:6379/0

# ---- Email (SMTP) ----
# SMTP_HOST=smtp.sendgrid.net
# SMTP_PORT=587
# SMTP_USER=apikey
# SMTP_PASSWORD=                      <-- put your SMTP password/API key here
# SMTP_FROM=noreply@yourdomain.com
# SMTP_USE_TLS=true

# ---- Webhooks ----
WEBHOOK_TIMEOUT_SECONDS=5
WEBHOOK_MAX_RETRIES=2

# ---- AI-detection gate ----
AQTIFY_AI_FLAG_THRESHOLD=10
AQTIFY_AI_BLOCK_THRESHOLD=60

# ---- App secret ----
APP_SECRET_KEY=                       <-- generate: python -c "import secrets; print(secrets.token_hex(32))"

# ---- TLS (only if not using a reverse proxy) ----
# SSL_KEYFILE=/path/to/privkey.pem
# SSL_CERTFILE=/path/to/fullchain.pem

# ---- Monitoring ----
# SENTRY_DSN=https://examplePublicKey@o0.ingest.sentry.io/0
LOG_LEVEL=INFO
LOG_FORMAT=json

# ---- Public base URL (badge/embed links) ----
PUBLIC_BASE_URL=http://127.0.0.1:8000
```

---

## Project structure

```
aqtify/
├── backend/
│   ├── api_server.py         FastAPI app — all routes, auth, RBAC, rate limiting
│   ├── config.py              central settings, reads .env
│   ├── auth.py                 API keys, RBAC, Redis/in-memory rate limiter
│   ├── pqsmap_engine.py       orchestrates the full pipeline incl. AI gate
│   ├── crypto_manager.py      ML-DSA-65 — server key + per-user standalone keys
│   ├── watermark.py            LSB watermark for images
│   ├── audio_watermark.py      LSB watermark for WAV PCM
│   ├── video_processor.py      ffmpeg frame sampling + video fingerprinting
│   ├── hash_utils.py            SHA-256 fingerprinting
│   ├── database.py             SQLAlchemy Core — SQLite or Postgres, same code
│   ├── media_processor.py      file type/metadata helpers
│   ├── deepfake_detector.py    heuristic AI-image triage (FFT/noise/color/EXIF)
│   ├── risk_scoring_engine.py
│   ├── report_generator.py
│   ├── manifest.py              C2PA-inspired manifest builder
│   ├── email_service.py        SMTP delivery, no-op if unconfigured
│   ├── webhook_service.py      HMAC-signed webhook delivery with retries
│   ├── badge.py                 public SVG badge + embed page generator
│   ├── logging_config.py       JSON logging + optional Sentry
│   ├── cli.py                   register/verify/keygen/sign from the terminal
│   ├── requirements.txt
│   └── .env.example             every configurable key, in one place
├── frontend/                    React 19 + Vite (see frontend/README.md)
│   └── src/
│       ├── panels/RegisterPanel.jsx / VerifyPanel.jsx / ReviewQueuePanel.jsx
│       └── components/, api/client.js
├── extension/                   Chrome/Edge extension (Manifest V3)
├── .gitignore
└── README.md
```

---

## Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # fill in whatever you want to turn on
uvicorn api_server:app --reload --port 8000
```

Requires **ffmpeg** on PATH for video/non-WAV audio support. A server
keypair is generated on first run and saved to `backend/keys/` — don't
delete it, or previously issued custodial certificates will stop verifying.

Every request to `/api/register*`, `/api/verify`, `/api/registry`,
`/api/custody`, `/api/manifest`, `/api/secured`, `/api/orgs*`, and
`/api/review-queue*` requires an `X-API-Key` header. `/api/badge` and
`/embed` are intentionally public (that's the point of a badge). Get a
key first:

```bash
curl -X POST http://127.0.0.1:8000/api/keys -F "user_name=Jane" -F "key_mode=server"
```

### Frontend

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173
```

See `frontend/README.md` for the component breakdown. Copy
`frontend/.env.example` to `.env` to point it at a non-default API URL.

### Browser extension

`chrome://extensions` → Developer mode → "Load unpacked" → select `extension/`.

### CLI

```bash
cd backend
python cli.py register path/to/photo.png "Jane Doe" "jane@example.com"
python cli.py verify   path/to/secured_media/AUTH-XXXXXXXXXX.png
python cli.py keygen                                          # self-sign flow
python cli.py sign <file_hash_to_sign> <private_key_b64>
```

---

## API reference

| Endpoint | Method | Auth | Notes |
|---|---|---|---|
| `/api/keys` | POST | none | create an API key (`key_mode=server`/`self-sign`, optional `org_id`) |
| `/api/orgs` | POST | ✅ | create an org, caller becomes owner |
| `/api/orgs/{id}/members` | GET/POST | ✅ (admin+ to add) | manage org membership + roles |
| `/api/orgs/{id}/webhook` | POST | ✅ (admin+) | set the org's webhook URL |
| `/api/orgs/{id}/records` | GET | ✅ (viewer+) | list all certificates registered under this org |
| `/api/register` | POST | ✅ | single-call custodial registration — runs the AI gate |
| `/api/register/bulk` | POST | ✅ | up to 50 files per call |
| `/api/register/prepare` / `/finalize` | POST | ✅ | self-sign two-step flow |
| `/api/verify` | POST | ✅ | full authenticity report |
| `/api/registry` | GET | ✅ | `?hash=` or `?certificate_id=` |
| `/api/custody/{cert}` | GET | ✅ | chain-of-custody log |
| `/api/manifest/{cert}` | GET | ✅ | C2PA-inspired manifest |
| `/api/secured/{cert}` | GET | ✅ | download the watermarked file |
| `/api/review-queue` | GET | ✅ | AI-flagged registrations pending review |
| `/api/review-queue/{cert}/resolve` | POST | ✅ | `decision=approved`/`rejected` |
| `/api/badge/{cert}.svg` | GET | **none** | embeddable status badge |
| `/embed/{cert}` | GET | **none** | standalone embed page |
| `/health` | GET | none | liveness probe (checks DB connectivity) |

Rate limit: 60 requests/minute per API key (Redis-backed if `REDIS_URL`
is set, in-memory otherwise).

---

## Cryptography & key modes

- **Algorithm:** ML-DSA-65 (FIPS 204 / CRYSTALS-Dilithium3), via `pqcrypto`.
- **Custodial ("server") mode:** the shared server keypair signs on your behalf.
- **Self-sign ("non-custodial") mode:** your own keypair, private key shown
  once, never stored server-side. Two-step `prepare`/`finalize` flow since
  you need the *post-watermark* hash before you can sign it.

## Watermarking & AI-detection gate

Invisible LSB steganography (images: RGB channels, audio: PCM samples,
video: an extracted keyframe). See `deepfake_detector.py` for the 4
heuristics (FFT frequency analysis, sensor-noise pattern, color
distribution, EXIF presence) combined into the AI-probability score that
now gates registration. It's still a heuristic, not a trained classifier
— expect false positives on real photos, which is exactly why the flag
threshold registers-but-queues instead of hard-blocking, and why both
thresholds are configurable.

## Chain of custody & C2PA-inspired manifest

Every register/verify action is logged per certificate
(`/api/custody/{cert}`). `/api/manifest/{cert}` returns a JSON document
structurally similar to a C2PA manifest — explicitly labeled
"C2PA-inspired," not "C2PA-compliant."

---

## What changed from the original (broken) repo, across this whole project

- Unified all module APIs so they actually match how they're called
- Server keypair persists to disk instead of regenerating on each run
- Hash/signature bound to the final distributable artifact, not the
  pre-watermark original — verifying your own file returns `AUTHENTIC`
- Replaced the random-number "deepfake detector" with real heuristics,
  now enforced automatically at registration instead of being a
  disconnected standalone endpoint
- Added API-key auth + rate limiting, per-user non-custodial keypairs,
  video/audio support, chain-of-custody, C2PA-inspired manifest, a
  browser extension, email delivery, webhooks, bulk registration,
  org/RBAC, a public badge widget, Postgres/Redis support, and
  structured logging/monitoring
- Rebuilt the frontend from a single-file HTML/CDN hack into a real
  Vite + React 19 project
- Removed several unintegrated stub modules from the original repo that
  weren't wired into anything

## Still not production-grade without

- [ ] A trained deepfake classifier (the heuristic detector will have a
      meaningfully higher false-positive rate than a trained model, which
      matters more now that it can block registrations)
- [ ] True in-container video watermark remuxing (currently: keyframe-only)
- [ ] Real C2PA SDK conformance
- [ ] Load testing / horizontal scaling validation
- [ ] A CI pipeline and automated test suite (this session's testing was
      manual `TestClient` runs, not a committed test suite)

## Security notes

- Custodial private keys never leave the server; self-sign private keys
  never touch the server at all.
- LSB watermarking is a deterrent/redundancy layer, not a cryptographic
  guarantee — the signed hash in the registry is the actual proof.
- Webhook payloads are HMAC-signed; verify the `X-Aqtify-Signature`
  header against your org's `webhook_secret` before trusting a payload.
- This is a hardened prototype, not an audited production system. Get an
  independent security review before using it anywhere a false verdict
  has real consequences.

## Author

**Janardan Kartikeya Agnihotram** — [GitHub](https://github.com/0kartik)
