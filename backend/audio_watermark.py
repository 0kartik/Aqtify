"""
Audio support for PQ-SMAP: LSB steganography in uncompressed WAV PCM
samples, mirroring the image watermarking approach. Like the PNG
requirement for images, this only survives on uncompressed WAV -- lossy
formats (mp3) are converted to WAV on registration, same tradeoff as
converting images to PNG.
"""

import shutil
import subprocess
import wave

DELIMITER = "<<<END>>>"


class AudioWatermark:

    def _ffmpeg_available(self):
        return shutil.which("ffmpeg") is not None

    def to_wav(self, input_path, output_path):
        """Convert any audio format ffmpeg understands to PCM WAV."""
        if not self._ffmpeg_available():
            raise RuntimeError("ffmpeg is required for audio conversion but was not found on PATH.")

        cmd = ["ffmpeg", "-y", "-i", input_path, "-ac", "1", "-ar", "44100", output_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg audio conversion failed: {result.stderr[-500:]}")
        return output_path

    def _text_to_bits(self, text):
        data = text.encode("utf-8")
        bits = []
        for byte in data:
            bits.extend([(byte >> i) & 1 for i in range(7, -1, -1)])
        return bits

    def _bits_to_text(self, bits):
        chars = []
        for i in range(0, len(bits) - 7, 8):
            byte = 0
            for bit in bits[i:i + 8]:
                byte = (byte << 1) | bit
            chars.append(byte)
        try:
            return bytes(chars).decode("utf-8", errors="ignore")
        except Exception:
            return ""

    def embed_watermark(self, wav_path, certificate_id, output_path):
        with wave.open(wav_path, "rb") as wf:
            params = wf.getparams()
            frames = bytearray(wf.readframes(wf.getnframes()))

        message = certificate_id + DELIMITER
        bits = self._text_to_bits(message)

        if len(bits) > len(frames):
            raise ValueError("Audio file too short to hold watermark payload.")

        for i, bit in enumerate(bits):
            frames[i] = (frames[i] & ~1) | bit

        with wave.open(output_path, "wb") as out:
            out.setparams(params)
            out.writeframes(bytes(frames))

        return output_path

    def extract_watermark(self, wav_path, max_bits=8 * 512):
        try:
            with wave.open(wav_path, "rb") as wf:
                frames = wf.readframes(min(wf.getnframes(), max_bits))
        except Exception:
            return None

        bits = [b & 1 for b in frames[:max_bits]]
        text = self._bits_to_text(bits)
        if DELIMITER in text:
            return text.split(DELIMITER)[0]
        return None
