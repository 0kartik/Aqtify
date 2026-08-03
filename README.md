<div align="center">

# Aqtify — PQ-SMAP

### Post-Quantum Secure Media Authentication Protocol

Cryptographically sign, watermark, and verify the authenticity of images, audio, and video using NIST-standardized post-quantum cryptography.

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](#)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi&logoColor=white)](#)
[![React](https://img.shields.io/badge/React_19-Frontend-61DAFB?logo=react&logoColor=black)](#)
[![ML-DSA-65](https://img.shields.io/badge/ML--DSA--65-FIPS_204-6E40C9)](#)
[![License](https://img.shields.io/badge/status-prototype-orange)](#)

</div>

---

## Overview

Aqtify (also referred to as **PQ-SMAP**) tackles a problem that gets harder every year: proving a piece of media is what it claims to be, in a world of AI-generated content and (eventually) quantum-capable adversaries.

Every file registered through Aqtify is:

1. **Screened** by a heuristic AI-content detector before it's ever allowed to register
2. **Watermarked** invisibly (LSB steganography across image, audio, and video formats)
3. **Fingerprinted** with SHA-256 and **signed** with **ML-DSA-65 (CRYSTALS-Dilithium3)** — a NIST FIPS 204 post-quantum signature algorithm
4. **Logged** into an immutable chain-of-custody, exportable as a **C2PA-inspired manifest**

The result is a certificate that can be independently re-verified at any time, backed by a signature that (unlike RSA/ECDSA) is designed to resist attacks from future quantum computers.

This is a full-stack, production-shaped system — not a notebook demo — spanning a FastAPI backend, a React 19 dashboard, a Chrome/Edge browser extension, and a CLI.

---

## Why this project is interesting

- **Real post-quantum cryptography, not a toy.** Uses `pqcrypto`'s ML-DSA-65 implementation for actual signing/verification, with both custodial (server-held key) and non-custodial (client-held key, never touches the server) modes.
- **Security-first design decisions.** The signed hash is bound to the *final watermarked artifact*, not the pre-processing original — so verifying a legitimately distributed file returns `AUTHENTIC` instead of failing on its own watermark. Non-custodial private keys are shown once and never persisted server-side.
- **Systems thinking beyond the crypto.** RBAC-scoped org accounts, HMAC-signed webhooks with retry logic, Redis-backed distributed rate limiting (falling back gracefully to in-memory), structured JSON logging, and a Postgres/SQLite-agnostic data layer via SQLAlchemy Core.
- **Honest about its limits.** The AI-detection gate is explicitly a heuristic (FFT frequency analysis, sensor-noise patterns, color distribution, EXIF presence) — documented as such, with a configurable flag/block threshold rather than a hard binary gate, precisely because heuristics produce false positives.

---

## Architecture

```
┌─────────────────┐       ┌─────────────────────────────────────┐
│  React Frontend  │◄────►│           FastAPI Backend           │
│  (Register /     │ REST │  ┌───────────────────────────────┐  │
│   Verify /       │      │  │  AI-detection gate            │  │
│   Review Queue)  │      │  │  → watermark → fingerprint    │  │
└─────────────────┘       │  │  → ML-DSA-65 sign → manifest  │  │
                          │  └───────────────────────────────┘  │
┌─────────────────┐       │  Auth · RBAC · Rate limiting        │
│Browser Extension│◄────► │  Webhooks · Email · Review queue    │
│  (Manifest V3)  │       └──────────────────┬───────────────── ┘
└─────────────────┘                          │
┌─────────────────┐               ┌──────────▼── ─ ───────┐
│ CLI (register / │               │ PostgreSQL / SQLite   │
│verify / keygen) │               │ Redis (rate limiting) │
└─────────────────┘               └───────────────────────┘
```

---

## Feature highlights

| Area | What it does |
|---|---|
| **AI-detection gate** | Every registration is screened; below threshold registers clean, mid-range queues for human review, above threshold is refused — both thresholds configurable |
| **Post-quantum signing** | ML-DSA-65 (FIPS 204) signatures, custodial or self-sign (non-custodial) key modes |
| **Watermarking** | Invisible LSB steganography across images (RGB channels), audio (PCM samples), and video (keyframe) |
| **Chain of custody** | Every register/verify action logged per certificate; exportable as a C2PA-inspired manifest |
| **Org accounts + RBAC** | `viewer < member < admin < owner` roles enforced across all org-scoped actions |
| **Webhooks** | HMAC-SHA256 signed `media.registered` / `media.verified` events, delivered with retries |
| **Bulk registration** | Up to 50 files per call, each independently gated and certified |
| **Public verification badge** | Embeddable, shields.io-style SVG badge + standalone embed page — no auth required |
| **Production hardening** | Postgres/Redis support, structured JSON logging, Sentry integration, `/health` liveness probe |
| **Multi-surface access** | REST API, React dashboard, Chrome/Edge extension, and terminal CLI all backed by the same engine |

---

## Tech stack

**Backend:** Python, FastAPI, SQLAlchemy Core (SQLite / PostgreSQL), Redis, `pqcrypto` (ML-DSA-65), ffmpeg
**Frontend:** React 19, Vite
**Extension:** Chrome/Edge, Manifest V3
**Infra:** Docker-ready, `.env`-driven config, structured logging, Sentry-compatible

---

## Quick start

### Backend

```bash
cd backend
python -m venv venv && venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn api_server:app --reload --port 8000
```

Runs with **zero configuration** out of the box (SQLite + in-memory rate limiting); Postgres, Redis, SMTP, webhooks, and Sentry are opt-in via `.env`.

### Frontend

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173
```

### CLI

```bash
python cli.py register path/to/photo.png "Jane Doe" "jane@example.com"
python cli.py verify   path/to/secured_media/AUTH-XXXXXXXXXX.png
```
## Engineering notes

- **Runtime-verified, not stubbed.** The full register → watermark → sign → verify pipeline was independently exercised end-to-end to confirm it produces real, re-verifiable signatures rather than mocked output.
- **Iterative hardening.** Started from a broken proof-of-concept with disconnected modules and a random-number "detector"; rebuilt into a coherent pipeline with real heuristics, persistent server keys, and a signature bound to the correct artifact.
- **Known gaps, tracked honestly:** no trained deepfake classifier yet (heuristic-only), video watermarking is currently keyframe-only rather than full remux, and there's no CI/automated test suite yet — all called out directly rather than glossed over, alongside a clear roadmap to close them.

---

## Author

**Kartikeya** — [GitHub](https://github.com/0kartik)
