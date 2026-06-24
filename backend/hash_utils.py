"""SHA-256 based media fingerprinting."""

import hashlib
from pathlib import Path


class HashUtils:

    CHUNK_SIZE = 65536

    @staticmethod
    def generate_file_hash(file_path, algorithm="sha256"):
        """Generate a hash for a file on disk, streamed in chunks."""

        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"{file_path} not found.")

        hasher = hashlib.new(algorithm)

        with open(file_path, "rb") as file:
            while chunk := file.read(HashUtils.CHUNK_SIZE):
                hasher.update(chunk)

        return hasher.hexdigest()

    @staticmethod
    def generate_bytes_hash(data: bytes, algorithm="sha256"):
        """Generate a hash for an in-memory bytes object."""

        hasher = hashlib.new(algorithm)
        hasher.update(data)
        return hasher.hexdigest()

    @staticmethod
    def generate_text_hash(text, algorithm="sha256"):

        hasher = hashlib.new(algorithm)
        hasher.update(text.encode())
        return hasher.hexdigest()

    @staticmethod
    def compare_hashes(hash1, hash2):
        return hash1 == hash2
