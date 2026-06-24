"""
Exports a C2PA-*inspired* manifest for a registered asset.

This mirrors the shape of a C2PA manifest (claim generator, assertions,
a hash-binding assertion, and a signature block) so it's structurally
familiar to anyone working with the real standard. It is NOT validated
against the C2PA conformance test suite and does not use the official
c2patool/SDK, so it should be labeled "C2PA-inspired" rather than
"C2PA-compliant" wherever it's shown to a person. True conformance would
mean adopting the C2PA SDK and a trust-list-anchored certificate, which is
a bigger lift than this endpoint -- see README roadmap.
"""


def build_manifest(record, crypto_algorithm, public_key_b64):
    return {
        "claim_generator": "Aqtify/PQ-SMAP 1.0",
        "manifest_type": "c2pa-inspired",
        "conformance": "NOT a certified C2PA manifest -- structurally similar, "
                        "not validated against the C2PA conformance suite",
        "title": record["file_name"],
        "instance_id": record["certificate_id"],
        "assertions": [
            {
                "label": "c2pa.hash.data",
                "algorithm": "sha256",
                "hash": record["file_hash"],
            },
            {
                "label": "stds.schema-org.CreativeWork",
                "author": record.get("owner_name") or "unknown",
                "email": record.get("owner_email"),
            },
            {
                "label": "aqtify.media_type",
                "value": record.get("media_type"),
            },
        ],
        "signature": {
            "algorithm": crypto_algorithm,
            "signer_key_mode": record.get("key_mode", "server"),
            "public_key_b64": public_key_b64,
            "signature_b64": record["signature"],
        },
        "created_at": record.get("created_at"),
    }
