"""
Core PQ-SMAP pipelines: register, verify, manifest, bulk registration.
Wires together hashing, post-quantum signing (server-custodial or
self-signed), watermarking, video/audio fingerprinting, the registry
database, chain-of-custody logging, the AI-detection registration gate,
risk scoring, email delivery, and webhook notifications.
"""

import json
import logging
import os
import tempfile
import uuid

from hash_utils import HashUtils
from crypto_manager import CryptoManager
from watermark import WatermarkManager
from audio_watermark import AudioWatermark
from video_processor import VideoProcessor
from database import DatabaseManager
from media_processor import MediaProcessor
from deepfake_detector import DeepfakeDetector
from risk_scoring_engine import RiskScoringEngine
from report_generator import ReportGenerator
from manifest import build_manifest
from config import settings
import email_service
import webhook_service

logger = logging.getLogger("aqtify.engine")

SECURED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "secured_media")
os.makedirs(SECURED_DIR, exist_ok=True)


class PQSMAPEngine:

    def __init__(self):
        self.crypto = CryptoManager()
        self.watermark = WatermarkManager()
        self.audio_watermark = AudioWatermark()
        self.video = VideoProcessor()
        self.database = DatabaseManager()
        self.media = MediaProcessor()
        self.detector = DeepfakeDetector()
        self.risk_engine = RiskScoringEngine()
        self.reporter = ReportGenerator()

    # -----------------------------------------------------------
    # AI-detection registration gate
    # -----------------------------------------------------------
    def _run_ai_gate(self, file_path, media_type):
        """
        Runs before anything else for images. Returns:
            (allowed: bool, ai_probability: int|None, review_status: str, block_reason: str|None)
        review_status is one of "clear" | "flagged" (still registers, queued for review).
        Videos/audio aren't screened (the heuristic detector only supports images).
        """
        if media_type != "image":
            return True, None, "clear", None

        result = self.detector.analyze_media(file_path)
        if not result.get("supported"):
            return True, None, "clear", None

        ai_probability = int(result.get("ai_probability", 0))

        if ai_probability > settings.AI_BLOCK_THRESHOLD:
            return (
                False, ai_probability, "rejected",
                f"AI-generation probability ({ai_probability}%) exceeds the block threshold "
                f"({settings.AI_BLOCK_THRESHOLD}%). Registration refused.",
            )

        if ai_probability > settings.AI_FLAG_THRESHOLD:
            return True, ai_probability, "flagged", None

        return True, ai_probability, "clear", None

    # -----------------------------------------------------------
    # Registration
    # -----------------------------------------------------------
    def register_media(self, file_path, owner_name=None, owner_email=None,
                        actor_key_id=None, signature_b64=None, public_key_b64=None,
                        org_id=None, send_email=True):
        """
        Single-call registration. Works for the default custodial ("server")
        key mode. If you pass signature_b64/public_key_b64 here they must
        already be a signature over the FINAL watermarked artifact's hash --
        which you can't know in advance in one call, so true self-sign
        registrations should use prepare_self_sign() / finalize_self_sign()
        instead (see below).
        """
        valid, info = self.media.validate_file(file_path)
        if not valid:
            return {"status": "error", "message": info}

        media_type = info

        allowed, ai_probability, review_status, block_reason = self._run_ai_gate(file_path, media_type)
        if not allowed:
            return {"status": "error", "message": block_reason, "ai_probability": ai_probability}

        file_name = os.path.basename(file_path)
        certificate_id = "AUTH-" + uuid.uuid4().hex[:10].upper()

        secured_path, watermark_embedded, file_hash, extra = self._process_media(
            file_path, certificate_id, media_type
        )

        return self._finalize_registration(
            file_hash, file_name, media_type, certificate_id,
            owner_name, owner_email, actor_key_id,
            signature_b64, public_key_b64, secured_path,
            watermark_embedded, extra=extra, org_id=org_id,
            ai_probability=ai_probability, review_status=review_status,
            send_email=send_email,
        )

    def register_bulk(self, files, owner_name=None, owner_email=None,
                       actor_key_id=None, org_id=None, send_email=True):
        """files: list of file paths. Returns a per-file result list -- one
        bad file doesn't abort the rest of the batch."""

        results = []
        for file_path in files:
            try:
                result = self.register_media(
                    file_path, owner_name=owner_name, owner_email=owner_email,
                    actor_key_id=actor_key_id, org_id=org_id, send_email=send_email,
                )
            except Exception as exc:
                result = {"status": "error", "message": str(exc)}
            result["file_name"] = os.path.basename(file_path)
            results.append(result)

        return {
            "status": "success",
            "total": len(files),
            "succeeded": sum(1 for r in results if r.get("status") == "success"),
            "failed": sum(1 for r in results if r.get("status") == "error"),
            "results": results,
        }

    def _process_media(self, file_path, certificate_id, media_type):
        """Watermark/fingerprint a file. Returns (secured_path, watermark_embedded, file_hash, extra)."""

        extra = {}

        if media_type == "image":
            output_path = os.path.join(SECURED_DIR, f"{certificate_id}.png")
            secured_path = self.watermark.embed_watermark(
                file_path, certificate_id, output_path
            )
            file_hash = HashUtils.generate_file_hash(secured_path)
            return secured_path, True, file_hash, extra

        if media_type == "audio":
            if file_path.lower().endswith(".wav"):
                wav_path = file_path
            else:
                wav_path = os.path.join(tempfile.gettempdir(), f"_pqsmap_{certificate_id}.wav")
                self.audio_watermark.to_wav(file_path, wav_path)
            output_path = os.path.join(SECURED_DIR, f"{certificate_id}.wav")
            secured_path = self.audio_watermark.embed_watermark(
                wav_path, certificate_id, output_path
            )
            if wav_path != file_path and os.path.exists(wav_path):
                os.remove(wav_path)
            file_hash = HashUtils.generate_file_hash(secured_path)
            return secured_path, True, file_hash, extra

        if media_type == "video":
            video_hash, first_frame_path, frame_count = self.video.compute_video_hash(file_path)
            keyframe_out = os.path.join(SECURED_DIR, f"{certificate_id}.png")
            secured_path = self.watermark.embed_watermark(
                first_frame_path, certificate_id, keyframe_out
            )
            if os.path.exists(first_frame_path):
                os.remove(first_frame_path)
            extra = {
                "video_hash_frame_count": frame_count,
                "duration_seconds": self.video.get_duration_seconds(file_path),
                "note": "Watermark is embedded in an extracted keyframe image, "
                        "not the video container -- see README limitations.",
            }
            return secured_path, True, video_hash, extra

        file_hash = HashUtils.generate_file_hash(file_path)
        return None, False, file_hash, extra

    # -----------------------------------------------------------
    # Two-step self-sign (non-custodial) registration
    # -----------------------------------------------------------
    def prepare_self_sign(self, file_path, owner_name=None, owner_email=None,
                           actor_key_id=None, org_id=None, send_email=True):
        """Step 1: watermark/fingerprint the file, return the hash to sign.
        Nothing is written to the public registry yet."""

        valid, info = self.media.validate_file(file_path)
        if not valid:
            return {"status": "error", "message": info}

        media_type = info

        allowed, ai_probability, review_status, block_reason = self._run_ai_gate(file_path, media_type)
        if not allowed:
            return {"status": "error", "message": block_reason, "ai_probability": ai_probability}

        file_name = os.path.basename(file_path)
        certificate_id = "AUTH-" + uuid.uuid4().hex[:10].upper()

        secured_path, watermark_embedded, file_hash, extra = self._process_media(
            file_path, certificate_id, media_type
        )

        if self.database.get_record_by_hash(file_hash):
            return {"status": "error", "message": "This exact file is already registered."}

        extra["_ai_probability"] = ai_probability
        extra["_review_status"] = review_status
        extra["_org_id"] = org_id
        extra["_send_email"] = send_email

        self.database.add_pending_registration(
            certificate_id=certificate_id,
            file_name=file_name,
            file_hash=file_hash,
            media_type=media_type,
            secured_path=secured_path,
            owner_name=owner_name,
            owner_email=owner_email,
            actor_key_id=actor_key_id,
            extra_json=json.dumps(extra),
        )

        return {
            "status": "pending",
            "certificate_id": certificate_id,
            "file_hash_to_sign": file_hash,
            "media_type": media_type,
            "watermark_embedded": watermark_embedded,
            "secured_file": secured_path,
            "ai_probability": ai_probability,
            "review_status": review_status,
            "next_step": (
                "Sign file_hash_to_sign with your own private key "
                "(python cli.py sign <hash> <private_key_b64>), then POST "
                "certificate_id + signature_b64 + public_key_b64 to /api/register/finalize."
            ),
        }

    def finalize_self_sign(self, certificate_id, signature_b64, public_key_b64):
        """Step 2: caller supplies their own signature over file_hash_to_sign."""

        pending = self.database.get_pending_registration(certificate_id)
        if pending is None:
            return {"status": "error", "message": "No pending registration for that certificate ID (expired or already finalized?)."}

        extra = json.loads(pending["extra_json"]) if pending["extra_json"] else {}
        ai_probability = extra.pop("_ai_probability", None)
        review_status = extra.pop("_review_status", "clear")
        org_id = extra.pop("_org_id", None)
        send_email = extra.pop("_send_email", True)

        result = self._finalize_registration(
            pending["file_hash"], pending["file_name"], pending["media_type"],
            pending["certificate_id"], pending["owner_name"], pending["owner_email"],
            pending["actor_key_id"], signature_b64, public_key_b64,
            pending["secured_path"], bool(pending["secured_path"]), extra=extra,
            org_id=org_id, ai_probability=ai_probability, review_status=review_status,
            send_email=send_email,
        )

        if result.get("status") == "success":
            self.database.delete_pending_registration(certificate_id)

        return result

    def _finalize_registration(self, file_hash, file_name, media_type, certificate_id,
                                owner_name, owner_email, actor_key_id,
                                signature_b64, public_key_b64, secured_path,
                                watermark_embedded, extra=None, org_id=None,
                                ai_probability=None, review_status="clear", send_email=True):

        if self.database.get_record_by_hash(file_hash):
            return {"status": "error", "message": "This exact file is already registered."}

        self_sign = bool(signature_b64 and public_key_b64)

        if self_sign:
            if not self.crypto.verify_with_key(public_key_b64, file_hash, signature_b64):
                return {
                    "status": "error",
                    "message": "Provided signature does not verify against the provided public key.",
                }
            key_mode = "self-sign"
            stored_public_key = public_key_b64
        else:
            signature = self.crypto.sign_hash(file_hash)
            signature_b64 = self.crypto.signature_to_b64(signature)
            key_mode = "server"
            stored_public_key = self.crypto.get_public_key_b64()

        self.database.add_media_record(
            certificate_id=certificate_id,
            file_name=file_name,
            file_hash=file_hash,
            signature=signature_b64,
            media_type=media_type,
            owner_name=owner_name,
            owner_email=owner_email,
            owner_key_id=actor_key_id,
            key_mode=key_mode,
            public_key=stored_public_key,
            org_id=org_id,
            ai_probability=ai_probability,
            review_status=review_status,
        )

        self.database.add_custody_entry(
            certificate_id=certificate_id,
            action="registered",
            actor_key_id=actor_key_id,
            actor_name=owner_name,
            detail=f"media_type={media_type}, key_mode={key_mode}, review_status={review_status}",
        )

        if review_status == "flagged":
            self.database.add_review_entry(
                certificate_id=certificate_id,
                ai_probability=ai_probability,
                reason=f"AI-generation probability {ai_probability}% exceeds flag threshold "
                       f"({settings.AI_FLAG_THRESHOLD}%) but not block threshold.",
            )

        result = {
            "status": "success",
            "certificate_id": certificate_id,
            "file_hash": file_hash,
            "media_type": media_type,
            "watermark_embedded": watermark_embedded,
            "secured_file": secured_path,
            "public_key": stored_public_key,
            "algorithm": self.crypto.ALGORITHM,
            "key_mode": key_mode,
            "ai_probability": ai_probability,
            "review_status": review_status,
        }
        if extra:
            result.update({k: v for k, v in extra.items() if not k.startswith("_")})

        # ---- email + webhook: best-effort, never fail the registration over these ----
        if send_email and owner_email:
            try:
                email_result = email_service.send_registration_email(
                    owner_email, certificate_id, file_name, secured_path, media_type,
                )
                result["email"] = email_result
            except Exception as exc:
                logger.warning("Email hook failed for %s: %s", certificate_id, exc)
                result["email"] = {"sent": False, "reason": str(exc)}

        if org_id:
            self._fire_webhook(org_id, "media.registered", {
                "certificate_id": certificate_id, "file_name": file_name,
                "media_type": media_type, "review_status": review_status,
                "ai_probability": ai_probability,
            })

        return result

    def _fire_webhook(self, org_id, event_type, data):
        try:
            org = self.database.get_organization(org_id)
            if org and org.get("webhook_url"):
                webhook_service.send_webhook(org["webhook_url"], org["webhook_secret"], event_type, data)
        except Exception as exc:
            logger.warning("Webhook hook failed for org %s event %s: %s", org_id, event_type, exc)

    # -----------------------------------------------------------
    # Verification
    # -----------------------------------------------------------
    def verify_media(self, file_path, certificate_id=None, actor_key_id=None):
        valid, info = self.media.validate_file(file_path)
        if not valid:
            return {"status": "error", "message": info}

        media_type = info
        file_name = os.path.basename(file_path)

        wav_tmp = None
        video_hash = None
        if media_type == "audio":
            if file_path.lower().endswith(".wav"):
                wav_tmp = file_path
            else:
                wav_tmp = os.path.join(tempfile.gettempdir(), f"_pqsmap_verify_{uuid.uuid4().hex[:6]}.wav")
                self.audio_watermark.to_wav(file_path, wav_tmp)
            hash_source = wav_tmp
        elif media_type == "video":
            video_hash, first_frame_path, _ = self.video.compute_video_hash(file_path)
            if os.path.exists(first_frame_path):
                os.remove(first_frame_path)
            hash_source = None
        else:
            hash_source = file_path

        current_hash = video_hash if media_type == "video" else HashUtils.generate_file_hash(hash_source)

        record = None
        if certificate_id:
            record = self.database.get_record_by_certificate(certificate_id)

        if record is None and media_type == "image":
            extracted_id = self.watermark.extract_watermark(file_path)
            if extracted_id:
                record = self.database.get_record_by_certificate(extracted_id)

        if record is None and media_type == "audio" and wav_tmp:
            extracted_id = self.audio_watermark.extract_watermark(wav_tmp)
            if extracted_id:
                record = self.database.get_record_by_certificate(extracted_id)

        if record is None:
            record = self.database.get_record_by_hash(current_hash)

        if wav_tmp and wav_tmp != file_path and os.path.exists(wav_tmp):
            os.remove(wav_tmp)

        if record is None:
            return {
                "status": "not_found",
                "message": "No authenticity record found for this media.",
                "file_hash": current_hash,
            }

        hash_valid = HashUtils.compare_hashes(current_hash, record["file_hash"])

        signature_valid = self.crypto.verify_with_key(
            record["public_key"] or self.crypto.get_public_key_b64(),
            record["file_hash"],
            record["signature"],
        )

        watermark_valid = True
        if media_type == "image":
            extracted_id = self.watermark.extract_watermark(file_path)
            watermark_valid = (extracted_id == record["certificate_id"])

        # AI probability is computed once, at registration time (the gate) --
        # verification reuses the stored value rather than re-running detection,
        # since the watermarked file's pixels differ slightly from the original.
        ai_report = {
            "supported": record.get("ai_probability") is not None,
            "ai_probability": record.get("ai_probability") or 0,
            "review_status": record.get("review_status", "clear"),
        }

        risk_score = self.risk_engine.calculate_score(
            hash_valid, signature_valid, watermark_valid,
            ai_report.get("ai_probability", 0),
        )
        risk_level = self.risk_engine.classify_risk(risk_score)

        report = self.reporter.generate_report(
            file_name=file_name,
            certificate_id=record["certificate_id"],
            file_hash=current_hash,
            hash_valid=hash_valid,
            signature_valid=signature_valid,
            watermark_valid=watermark_valid,
            owner_name=record["owner_name"],
            ai_report=ai_report,
            risk_score=risk_score,
            risk_level=risk_level,
        )

        self.database.add_verification_record(
            certificate_id=record["certificate_id"],
            file_hash=current_hash,
            status=report["overall_status"],
            risk_score=risk_score,
        )

        self.database.add_custody_entry(
            certificate_id=record["certificate_id"],
            action="verified",
            actor_key_id=actor_key_id,
            detail=f"result={report['overall_status']}, score={risk_score}",
        )

        report["status"] = "success"
        report["key_mode"] = record.get("key_mode", "server")

        if record.get("org_id"):
            self._fire_webhook(record["org_id"], "media.verified", {
                "certificate_id": record["certificate_id"],
                "overall_status": report["overall_status"],
                "risk_score": risk_score,
            })

        return report

    # -----------------------------------------------------------
    # Registry lookup / chain of custody / review queue
    # -----------------------------------------------------------
    def lookup(self, file_hash=None, certificate_id=None):
        record = None
        if certificate_id:
            record = self.database.get_record_by_certificate(certificate_id)
        elif file_hash:
            record = self.database.get_record_by_hash(file_hash)

        if record is None:
            return {"status": "not_found"}

        history = self.database.get_verification_history(record["certificate_id"])
        return {"status": "success", "record": record, "history": history}

    def list_by_key(self, key_id):
        return {"status": "success", "records": self.database.list_records_by_key(key_id)}

    def public_verify(self, certificate_id=None, file_hash=None):
        """No-auth lookup for the public verification page / badge. Only
        returns fields safe to expose publicly -- no owner email, no
        signature, no internal key ids."""
        record = None
        if certificate_id:
            record = self.database.get_record_by_certificate(certificate_id)
        elif file_hash:
            record = self.database.get_record_by_hash(file_hash)

        if record is None:
            return {"status": "not_found"}

        status_label = "TAMPERED" if record.get("review_status") == "rejected" else "AUTHENTIC"
        return {
            "status": "success",
            "certificate_id": record["certificate_id"],
            "file_name": record["file_name"],
            "media_type": record["media_type"],
            "created_at": record["created_at"],
            "owner_name": record.get("owner_name"),
            "review_status": record.get("review_status"),
            "verification_status": status_label,
            "algorithm": self.crypto.ALGORITHM,
        }

    def custody_log(self, certificate_id):
        record = self.database.get_record_by_certificate(certificate_id)
        if record is None:
            return {"status": "not_found"}
        log = self.database.get_custody_log(certificate_id)
        return {"status": "success", "certificate_id": certificate_id, "log": log}

    def get_review_queue(self, status="pending"):
        return {"status": "success", "queue": self.database.get_review_queue(status)}

    def resolve_review(self, certificate_id, decision, reviewed_by):
        if decision not in ("approved", "rejected"):
            return {"status": "error", "message": "decision must be 'approved' or 'rejected'"}
        record = self.database.get_record_by_certificate(certificate_id)
        if record is None:
            return {"status": "not_found"}
        self.database.resolve_review_entry(certificate_id, decision, reviewed_by)
        self.database.add_custody_entry(
            certificate_id=certificate_id, action="review_" + decision,
            actor_key_id=reviewed_by, detail=f"manual review resolved: {decision}",
        )
        return {"status": "success", "certificate_id": certificate_id, "decision": decision}

    # -----------------------------------------------------------
    # C2PA-inspired manifest export
    # -----------------------------------------------------------
    def get_manifest(self, certificate_id):
        record = self.database.get_record_by_certificate(certificate_id)
        if record is None:
            return {"status": "not_found"}

        manifest = build_manifest(
            record, self.crypto.ALGORITHM,
            record["public_key"] or self.crypto.get_public_key_b64(),
        )
        manifest["status"] = "success"
        return manifest
