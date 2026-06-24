from datetime import datetime


class ReportGenerator:

    def generate_report(self, file_name, certificate_id, file_hash,
                         hash_valid, signature_valid, watermark_valid,
                         owner_name, ai_report, risk_score, risk_level):

        overall_status = "AUTHENTIC" if (
            hash_valid and signature_valid and risk_score >= 70
        ) else ("TAMPERED" if not hash_valid else "UNTRUSTED")

        return {
            "timestamp": str(datetime.now()),
            "file_name": file_name,
            "certificate_id": certificate_id,
            "file_hash": file_hash,
            "owner": owner_name,
            "checks": {
                "hash_valid": hash_valid,
                "signature_valid": signature_valid,
                "watermark_valid": watermark_valid,
            },
            "ai_analysis": ai_report,
            "authenticity_score": risk_score,
            "risk_level": risk_level,
            "overall_status": overall_status,
        }
