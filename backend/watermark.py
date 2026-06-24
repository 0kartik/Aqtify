"""
Invisible watermarking via LSB (least-significant-bit) steganography.

The certificate ID is embedded into the least-significant bit of each
color channel across the image's pixels. Because LSB embedding does not
survive lossy re-compression, the output is always saved as PNG -- this
is Layer 2 of PQ-SMAP's redundancy model (Layer 1 = EXIF, Layer 3 = the
database registry, which remains the ground truth either way).
"""

from PIL import Image

DELIMITER = "<<<END>>>"


class WatermarkManager:

    def _text_to_bits(self, text: str):
        data = text.encode("utf-8")
        bits = []
        for byte in data:
            bits.extend([(byte >> i) & 1 for i in range(7, -1, -1)])
        return bits

    def _bits_to_text(self, bits):
        chars = []
        for i in range(0, len(bits) - 7, 8):
            byte_bits = bits[i:i + 8]
            byte = 0
            for bit in byte_bits:
                byte = (byte << 1) | bit
            chars.append(byte)
        try:
            return bytes(chars).decode("utf-8", errors="ignore")
        except Exception:
            return ""

    def embed_watermark(self, image_path, certificate_id, output_path):
        """Embed `certificate_id` invisibly into the image and save as PNG."""

        image = Image.open(image_path).convert("RGB")
        pixels = image.load()
        width, height = image.size

        message = certificate_id + DELIMITER
        bits = self._text_to_bits(message)

        capacity = width * height * 3
        if len(bits) > capacity:
            raise ValueError("Image too small to hold watermark payload.")

        bit_index = 0
        for y in range(height):
            for x in range(width):
                if bit_index >= len(bits):
                    break
                r, g, b = pixels[x, y]
                channels = [r, g, b]
                for c in range(3):
                    if bit_index < len(bits):
                        channels[c] = (channels[c] & ~1) | bits[bit_index]
                        bit_index += 1
                pixels[x, y] = tuple(channels)
            if bit_index >= len(bits):
                break

        if not output_path.lower().endswith(".png"):
            output_path = output_path.rsplit(".", 1)[0] + ".png"

        image.save(output_path, "PNG")
        return output_path

    def extract_watermark(self, image_path):
        """Extract the embedded certificate ID, or None if absent/unreadable."""

        try:
            image = Image.open(image_path).convert("RGB")
        except Exception:
            return None

        pixels = image.load()
        width, height = image.size

        bits = []
        # Cap the scan so we don't read gigantic images bit-by-bit forever.
        max_bits = min(width * height * 3, 8 * 2048)

        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                bits.extend([r & 1, g & 1, b & 1])
                if len(bits) >= max_bits:
                    break
            if len(bits) >= max_bits:
                break

        text = self._bits_to_text(bits)
        if DELIMITER in text:
            return text.split(DELIMITER)[0]
        return None

    def verify_image_readable(self, image_path):
        try:
            image = Image.open(image_path)
            image.verify()
            return True
        except Exception:
            return False
