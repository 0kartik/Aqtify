import os
import shutil
import uuid

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response, HTMLResponse

from pqsmap_engine import PQSMAPEngine, SECURED_DIR
from auth import generate_api_key, require_api_key, require_org_role, new_webhook_secret
from config import settings
from logging_config import setup_logging
import badge

setup_logging()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = FastAPI(title="PQ-SMAP API", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = PQSMAPEngine()
auth_dependency = require_api_key(engine.database)


def _save_upload(file: UploadFile) -> str:
    safe_name = f"{uuid.uuid4().hex[:8]}_{file.filename}"
    file_path = os.path.join(UPLOAD_FOLDER, safe_name)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return file_path


@app.get("/")
def home():
    return {
        "message": "PQ-SMAP API running",
        "algorithm": engine.crypto.ALGORITHM,
        "auth_required": True,
        "ai_gate": {
            "flag_threshold": settings.AI_FLAG_THRESHOLD,
            "block_threshold": settings.AI_BLOCK_THRESHOLD,
        },
        "note": "Create an API key at POST /api/keys before calling register/verify.",
    }


@app.get("/health")
def health():
    """Liveness/readiness probe -- checks DB connectivity."""
    try:
        with engine.database.get_connection() as conn:
            conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False
    return {"status": "ok" if db_ok else "degraded", "database": db_ok}


# -----------------------------------------------------------
# API keys
# -----------------------------------------------------------
@app.post("/api/keys")
def create_api_key(
    user_name: str = Form(None),
    user_email: str = Form(None),
    key_mode: str = Form("server"),
    org_id: str = Form(None),
):
    """
    key_mode="server"    custodial -- easiest, server signs on your behalf.
    key_mode="self-sign" non-custodial -- returns a fresh ML-DSA-65 keypair;
                          the private key is shown ONCE and never stored.
    org_id: optional -- join an existing organization as a "member".
            (Use /api/orgs to create one and get owner-level access.)
    """
    if key_mode not in ("server", "self-sign"):
        raise HTTPException(status_code=400, detail="key_mode must be 'server' or 'self-sign'")

    public_key_b64 = None
    private_key_b64 = None
    if key_mode == "self-sign":
        from crypto_manager import CryptoManager
        keys = CryptoManager.generate_standalone_keypair_b64()
        public_key_b64 = keys["public_key_b64"]
        private_key_b64 = keys["private_key_b64"]

    role = "member" if org_id else "owner"
    result = generate_api_key(
        engine.database, user_name=user_name, user_email=user_email,
        key_mode=key_mode, public_key_b64=public_key_b64, org_id=org_id, role=role,
    )
    if org_id:
        engine.database.add_org_member(org_id, result["key_id"], role=role)

    if private_key_b64:
        result["private_key_b64"] = private_key_b64
        result["public_key_b64"] = public_key_b64
        result["warning"] = ("This private key is shown ONCE and is not stored on the "
                              "server. Save it now -- you'll need it to sign every "
                              "registration under this key.")
    return result


# -----------------------------------------------------------
# Organizations / RBAC
# -----------------------------------------------------------
@app.post("/api/orgs")
def create_org(name: str = Form(...), key=Depends(auth_dependency)):
    """Create an organization and promote the calling key to its owner."""
    org_id = "org_" + uuid.uuid4().hex[:10]
    webhook_secret = new_webhook_secret()
    engine.database.create_organization(org_id, name, webhook_url=None, webhook_secret=webhook_secret)
    engine.database.set_api_key_org(key["key_id"], org_id, role="owner")
    engine.database.add_org_member(org_id, key["key_id"], role="owner")
    return {"org_id": org_id, "name": name, "webhook_secret": webhook_secret, "your_role": "owner"}


@app.get("/api/orgs/{org_id}/members")
def list_org_members(org_id: str, key=Depends(auth_dependency)):
    require_org_role("viewer")(key)
    if key["org_id"] != org_id:
        raise HTTPException(status_code=403, detail="Not a member of this organization.")
    return {"org_id": org_id, "members": engine.database.get_org_members(org_id)}


@app.post("/api/orgs/{org_id}/members")
def add_org_member(org_id: str, member_key_id: str = Form(...), role: str = Form("member"),
                    key=Depends(auth_dependency)):
    """Add an existing API key to this org. Requires 'admin' or higher."""
    require_org_role("admin")(key)
    if key["org_id"] != org_id:
        raise HTTPException(status_code=403, detail="Not a member of this organization.")
    if role not in ("viewer", "member", "admin", "owner"):
        raise HTTPException(status_code=400, detail="Invalid role.")
    engine.database.set_api_key_org(member_key_id, org_id, role=role)
    engine.database.add_org_member(org_id, member_key_id, role=role)
    return {"status": "success", "org_id": org_id, "member_key_id": member_key_id, "role": role}


@app.post("/api/orgs/{org_id}/webhook")
def set_org_webhook(org_id: str, webhook_url: str = Form(...), key=Depends(auth_dependency)):
    """Set/replace this org's webhook URL. Requires 'admin' or higher.
    Fires media.registered and media.verified events, HMAC-signed with the
    org's webhook_secret (returned when the org was created)."""
    require_org_role("admin")(key)
    if key["org_id"] != org_id:
        raise HTTPException(status_code=403, detail="Not a member of this organization.")
    org = engine.database.get_organization(org_id)
    if org is None:
        raise HTTPException(status_code=404, detail="Organization not found.")
    engine.database.set_org_webhook(org_id, webhook_url, org["webhook_secret"])
    return {"status": "success", "org_id": org_id, "webhook_url": webhook_url}


@app.get("/api/orgs/{org_id}/records")
def list_org_records(org_id: str, key=Depends(auth_dependency)):
    require_org_role("viewer")(key)
    if key["org_id"] != org_id:
        raise HTTPException(status_code=403, detail="Not a member of this organization.")
    return {"org_id": org_id, "records": engine.database.list_records_by_org(org_id)}


# -----------------------------------------------------------
# Register / verify (require an API key + are rate-limited)
# -----------------------------------------------------------
@app.post("/api/register")
async def register_media(
    file: UploadFile = File(...),
    owner_name: str = Form(None),
    owner_email: str = Form(None),
    signature_b64: str = Form(None),
    public_key_b64: str = Form(None),
    send_email: bool = Form(True),
    key=Depends(auth_dependency),
):
    """AI-detection gate applies automatically: images are screened, and
    registration is refused outright above AQTIFY_AI_BLOCK_THRESHOLD (see
    .env.example) or flagged for manual review above AQTIFY_AI_FLAG_THRESHOLD.
    If owner_email is set and SMTP is configured, the secured file is emailed
    to them (send_email=false to skip)."""

    file_path = _save_upload(file)
    try:
        result = engine.register_media(
            file_path, owner_name, owner_email,
            actor_key_id=key["key_id"],
            signature_b64=signature_b64,
            public_key_b64=public_key_b64,
            org_id=key.get("org_id"),
            send_email=send_email,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result["message"])

    return result


@app.post("/api/register/bulk")
async def register_bulk(
    files: list[UploadFile] = File(...),
    owner_name: str = Form(None),
    owner_email: str = Form(None),
    send_email: bool = Form(True),
    key=Depends(auth_dependency),
):
    """Register multiple files in one call. Each file gets its own AI gate
    check and certificate; one bad file doesn't abort the rest of the batch."""

    if len(files) > 50:
        raise HTTPException(status_code=400, detail="Max 50 files per bulk request.")

    paths = [_save_upload(f) for f in files]
    try:
        result = engine.register_bulk(
            paths, owner_name=owner_name, owner_email=owner_email,
            actor_key_id=key["key_id"], org_id=key.get("org_id"), send_email=send_email,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return result


@app.post("/api/register/prepare")
async def prepare_registration(
    file: UploadFile = File(...),
    owner_name: str = Form(None),
    owner_email: str = Form(None),
    send_email: bool = Form(True),
    key=Depends(auth_dependency),
):
    """Step 1 of the self-sign (non-custodial) flow: runs the AI gate,
    watermarks/fingerprints the file, and returns the hash you need to sign
    with your own private key. Nothing is added to the public registry
    until you call /api/register/finalize."""

    file_path = _save_upload(file)
    try:
        result = engine.prepare_self_sign(
            file_path, owner_name, owner_email, actor_key_id=key["key_id"],
            org_id=key.get("org_id"), send_email=send_email,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result["message"])

    return result


@app.post("/api/register/finalize")
async def finalize_registration(
    certificate_id: str = Form(...),
    signature_b64: str = Form(...),
    public_key_b64: str = Form(...),
    key=Depends(auth_dependency),
):
    """Step 2 of the self-sign flow: submit your signature over the hash
    returned by /api/register/prepare."""

    try:
        result = engine.finalize_self_sign(certificate_id, signature_b64, public_key_b64)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result["message"])

    return result


@app.post("/api/verify")
async def verify_media(
    file: UploadFile = File(...),
    certificate_id: str = Form(None),
    key=Depends(auth_dependency),
):
    file_path = _save_upload(file)
    try:
        result = engine.verify_media(file_path, certificate_id, actor_key_id=key["key_id"])
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result["message"])

    return result


# -----------------------------------------------------------
# Registry / chain of custody / C2PA-inspired manifest
# -----------------------------------------------------------
@app.get("/api/registry")
def registry_lookup(
    hash: str = Query(None),
    certificate_id: str = Query(None),
    key=Depends(auth_dependency),
):
    if not hash and not certificate_id:
        raise HTTPException(status_code=400, detail="Provide either hash or certificate_id")
    result = engine.lookup(file_hash=hash, certificate_id=certificate_id)
    if result["status"] == "not_found":
        raise HTTPException(status_code=404, detail="No matching record found")
    return result


@app.get("/api/custody/{certificate_id}")
def custody_log(certificate_id: str, key=Depends(auth_dependency)):
    result = engine.custody_log(certificate_id)
    if result["status"] == "not_found":
        raise HTTPException(status_code=404, detail="No matching record found")
    return result


@app.get("/api/manifest/{certificate_id}")
def manifest(certificate_id: str, key=Depends(auth_dependency)):
    result = engine.get_manifest(certificate_id)
    if result["status"] == "not_found":
        raise HTTPException(status_code=404, detail="No matching record found")
    return result


@app.get("/api/secured/{certificate_id}")
def download_secured(certificate_id: str, key=Depends(auth_dependency)):
    for ext in (".png", ".wav"):
        path = os.path.join(SECURED_DIR, f"{certificate_id}{ext}")
        if os.path.exists(path):
            media_type = "image/png" if ext == ".png" else "audio/wav"
            return FileResponse(path, media_type=media_type, filename=f"{certificate_id}{ext}")
    raise HTTPException(status_code=404, detail="Secured file not found")


# -----------------------------------------------------------
# Review queue (AI-detection gate)
# -----------------------------------------------------------
@app.get("/api/review-queue")
def review_queue(status: str = Query("pending"), key=Depends(auth_dependency)):
    return engine.get_review_queue(status)


@app.post("/api/review-queue/{certificate_id}/resolve")
def resolve_review(certificate_id: str, decision: str = Form(...), key=Depends(auth_dependency)):
    result = engine.resolve_review(certificate_id, decision, reviewed_by=key["key_id"])
    if result.get("status") == "not_found":
        raise HTTPException(status_code=404, detail="No matching record found")
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


# -----------------------------------------------------------
# Public badge / embed widget -- NO auth (meant for embedding anywhere)
# -----------------------------------------------------------
# -----------------------------------------------------------
# Personal dashboard (registrations made with the calling key)
# -----------------------------------------------------------
@app.get("/api/my-registrations")
def my_registrations(key=Depends(auth_dependency)):
    return engine.list_by_key(key["key_id"])


# -----------------------------------------------------------
# Public verification search -- NO auth, safe-fields-only, meant for
# anyone (not just API key holders) to check a claim.
# -----------------------------------------------------------
@app.get("/api/public-verify")
def public_verify(certificate_id: str = Query(None), hash: str = Query(None)):
    if not certificate_id and not hash:
        raise HTTPException(status_code=400, detail="Provide either certificate_id or hash")
    result = engine.public_verify(certificate_id=certificate_id, file_hash=hash)
    if result["status"] == "not_found":
        raise HTTPException(status_code=404, detail="No matching record found")
    return result


@app.get("/api/badge/{certificate_id}.svg")
def get_badge(certificate_id: str):
    record = engine.database.get_record_by_certificate(certificate_id)
    status_label = "UNKNOWN" if record is None else (
        "TAMPERED" if record.get("review_status") == "rejected" else "AUTHENTIC"
    )
    svg = badge.build_badge_svg(status_label)
    return Response(content=svg, media_type="image/svg+xml")


@app.get("/embed/{certificate_id}")
def get_embed_page(certificate_id: str):
    record = engine.database.get_record_by_certificate(certificate_id)
    status_label = "UNKNOWN" if record is None else "AUTHENTIC"
    html = badge.build_embed_html(certificate_id, status_label, settings.PUBLIC_BASE_URL)
    return HTMLResponse(content=html)
