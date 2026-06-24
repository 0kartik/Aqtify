"""
Post-quantum digital signatures using ML-DSA-65 (the NIST-standardized
version of CRYSTALS-Dilithium3), via the `pqcrypto` library.

A single server keypair is generated once and persisted to disk under
`keys/`, so signatures created on one run can be verified on the next.
"""

import base64
import os

from pqcrypto.sign.ml_dsa_65 import generate_keypair, sign, verify

KEY_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys")
PUBLIC_KEY_PATH = os.path.join(KEY_DIR, "public_key.bin")
PRIVATE_KEY_PATH = os.path.join(KEY_DIR, "private_key.bin")


class CryptoManager:
    """Wraps ML-DSA-65 keypair generation, signing and verification."""

    ALGORITHM = "ML-DSA-65 (CRYSTALS-Dilithium3)"

    def __init__(self, auto_load=True):
        self.public_key = None
        self.private_key = None

        if auto_load:
            self.load_or_generate_keys()

    def load_or_generate_keys(self):
        """Load the persisted server keypair, generating one on first run."""

        os.makedirs(KEY_DIR, exist_ok=True)

        if os.path.exists(PUBLIC_KEY_PATH) and os.path.exists(PRIVATE_KEY_PATH):
            with open(PUBLIC_KEY_PATH, "rb") as f:
                self.public_key = f.read()
            with open(PRIVATE_KEY_PATH, "rb") as f:
                self.private_key = f.read()
        else:
            self.generate_keys()
            with open(PUBLIC_KEY_PATH, "wb") as f:
                f.write(self.public_key)
            with open(PRIVATE_KEY_PATH, "wb") as f:
                f.write(self.private_key)

    def generate_keys(self):
        """Generate a fresh ML-DSA-65 key pair (does not persist it)."""

        self.public_key, self.private_key = generate_keypair()

    def sign_hash(self, file_hash: str) -> bytes:
        """Sign a hex digest string, returning raw signature bytes."""

        if self.private_key is None:
            raise ValueError("Keys not loaded/generated.")

        return sign(self.private_key, file_hash.encode())

    def verify_signature(self, file_hash: str, signature: bytes) -> bool:
        """Verify a signature over a hex digest string."""

        if self.public_key is None:
            raise ValueError("Keys not loaded/generated.")

        try:
            return bool(verify(self.public_key, file_hash.encode(), signature))
        except Exception:
            return False

    def get_public_key(self) -> bytes:
        return self.public_key

    def get_public_key_b64(self) -> str:
        return base64.b64encode(self.public_key).decode()

    @staticmethod
    def signature_to_b64(signature: bytes) -> str:
        return base64.b64encode(signature).decode()

    @staticmethod
    def signature_from_b64(signature_b64: str) -> bytes:
        return base64.b64decode(signature_b64)

    # -----------------------------------------------------------
    # Standalone (per-user, non-custodial) keypairs
    # -----------------------------------------------------------
    @staticmethod
    def generate_standalone_keypair_b64():
        """Generate a fresh keypair not tied to this instance, base64-encoded.

        Used for self-sign accounts: the private key is returned once to the
        caller and never persisted server-side.
        """
        public_key, private_key = generate_keypair()
        return {
            "public_key_b64": base64.b64encode(public_key).decode(),
            "private_key_b64": base64.b64encode(private_key).decode(),
        }

    @staticmethod
    def sign_with_key(private_key_b64: str, file_hash: str) -> str:
        private_key = base64.b64decode(private_key_b64)
        signature = sign(private_key, file_hash.encode())
        return base64.b64encode(signature).decode()

    @staticmethod
    def verify_with_key(public_key_b64: str, file_hash: str, signature_b64: str) -> bool:
        try:
            public_key = base64.b64decode(public_key_b64)
            signature = base64.b64decode(signature_b64)
            return bool(verify(public_key, file_hash.encode(), signature))
        except Exception:
            return False
