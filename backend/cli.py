"""
Simple CLI for exercising the PQ-SMAP engine directly, no server needed.

Usage:
    python cli.py register path/to/image.png [owner_name] [owner_email]
    python cli.py verify path/to/file.png [certificate_id]

Note: AI-detection now runs automatically as part of `register` (the
AI-detection gate) -- there's no separate detect command anymore.

Self-sign (non-custodial) flow -- your private key never touches the server:
    python cli.py keygen
    python cli.py hash path/to/watermarked_file.png
    python cli.py sign <file_hash> <private_key_b64>
    # then POST to /api/register with signature_b64 + public_key_b64 set
"""

import json
import sys

from crypto_manager import CryptoManager
from hash_utils import HashUtils
from pqsmap_engine import PQSMAPEngine


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    # ---- self-sign (non-custodial) commands: no engine needed ----
    if command == "keygen":
        keys = CryptoManager.generate_standalone_keypair_b64()
        print(json.dumps(keys, indent=2))
        print(
            "\nSave the private_key_b64 somewhere safe -- it is shown once and "
            "never stored on the server. Use it with `python cli.py sign` to "
            "produce a signature for /api/register.",
            file=sys.stderr,
        )
        return

    if command == "sign":
        if len(sys.argv) < 4:
            print("Usage: python cli.py sign <file_hash> <private_key_b64>")
            sys.exit(1)
        file_hash, private_key_b64 = sys.argv[2], sys.argv[3]
        signature_b64 = CryptoManager.sign_with_key(private_key_b64, file_hash)
        print(signature_b64)
        return

    if command == "hash":
        if len(sys.argv) < 3:
            print("Usage: python cli.py hash <file_path>")
            sys.exit(1)
        print(HashUtils.generate_file_hash(sys.argv[2]))
        return

    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    file_path = sys.argv[2]
    engine = PQSMAPEngine()

    if command == "register":
        owner_name = sys.argv[3] if len(sys.argv) > 3 else None
        owner_email = sys.argv[4] if len(sys.argv) > 4 else None
        result = engine.register_media(file_path, owner_name, owner_email)

    elif command == "verify":
        certificate_id = sys.argv[3] if len(sys.argv) > 3 else None
        result = engine.verify_media(file_path, certificate_id)

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
