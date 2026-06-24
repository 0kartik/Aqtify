"""
Lightweight heuristic AI-generated-image detector.

This is NOT a trained classifier -- it is a set of statistical signals
that tend to differ between camera-captured photos and GAN/diffusion
output, combined into a single confidence score. It is meant as a
first-pass triage signal, not a forensic verdict.

Methods:
  1. FFT frequency analysis   - GAN upsampling leaves periodic spectral spikes
  2. Noise pattern analysis   - real sensor noise is high-frequency and uneven;
                                 synthetic images are often unusually smooth
  3. Color distribution       - synthetic images often have unnaturally
                                 uniform saturation/hue histograms
  4. Metadata presence        - real camera photos usually carry EXIF data;
                                 its total absence is a weak AI signal
"""

import numpy as np
from PIL import Image, ExifTags


class DeepfakeDetector:

    def _fft_score(self, gray: np.ndarray) -> float:
        """Higher score = more periodic/artificial high-frequency energy."""

        f = np.fft.fft2(gray)
        fshift = np.fft.fftshift(f)
        magnitude = np.log(np.abs(fshift) + 1)

        h, w = magnitude.shape
        cy, cx = h // 2, w // 2
        radius = min(h, w) // 8

        y, x = np.ogrid[:h, :w]
        mask_outer = (x - cx) ** 2 + (y - cy) ** 2 > radius ** 2

        outer_energy = magnitude[mask_outer].mean()
        total_energy = magnitude.mean() + 1e-6

        ratio = outer_energy / total_energy
        # Normalize roughly into 0-100
        return float(np.clip((ratio - 0.9) * 300, 0, 100))

    def _noise_score(self, gray: np.ndarray) -> float:
        """Higher score = suspiciously smooth / low natural sensor noise."""

        diffs = np.abs(np.diff(gray.astype(np.float32), axis=0))
        noise_level = diffs.std()

        # Real photos typically have noise_level well above ~2.5
        score = np.clip((6.0 - noise_level) * 15, 0, 100)
        return float(score)

    def _color_score(self, rgb: np.ndarray) -> float:
        """Higher score = unnaturally uniform saturation distribution."""

        r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
        maxc = np.max(rgb, axis=-1).astype(np.float32)
        minc = np.min(rgb, axis=-1).astype(np.float32)
        sat = np.where(maxc > 0, (maxc - minc) / (maxc + 1e-6), 0)

        std_sat = sat.std()
        score = np.clip((0.18 - std_sat) * 400, 0, 100)
        return float(score)

    def _metadata_score(self, image: Image.Image) -> float:
        """Higher score = missing camera/lens EXIF metadata."""

        try:
            exif = image.getexif()
            if not exif or len(exif) == 0:
                return 60.0
            keys = {ExifTags.TAGS.get(k, k) for k in exif.keys()}
            if "Make" not in keys and "Model" not in keys:
                return 40.0
            return 5.0
        except Exception:
            return 50.0

    def analyze_media(self, file_path):
        """Run heuristic AI-detection over an image file."""

        try:
            image = Image.open(file_path)
            rgb_image = image.convert("RGB")
        except Exception as exc:
            return {
                "supported": False,
                "error": f"Could not analyze file: {exc}",
                "ai_probability": 0,
                "verdict": "UNKNOWN",
                "methods": {},
            }

        arr = np.array(rgb_image).astype(np.float32)
        gray = np.array(rgb_image.convert("L")).astype(np.float32)

        methods = {
            "fft_frequency_analysis": round(self._fft_score(gray), 1),
            "noise_pattern_analysis": round(self._noise_score(gray), 1),
            "color_distribution_analysis": round(self._color_score(arr), 1),
            "metadata_absence_analysis": round(self._metadata_score(image), 1),
        }

        weights = {
            "fft_frequency_analysis": 0.30,
            "noise_pattern_analysis": 0.30,
            "color_distribution_analysis": 0.20,
            "metadata_absence_analysis": 0.20,
        }

        ai_probability = sum(methods[k] * weights[k] for k in weights)
        ai_probability = round(min(max(ai_probability, 0), 100), 1)

        if ai_probability > 70:
            verdict = "LIKELY AI-GENERATED"
        elif ai_probability > 40:
            verdict = "SUSPICIOUS"
        else:
            verdict = "LIKELY AUTHENTIC"

        return {
            "supported": True,
            "ai_probability": ai_probability,
            "verdict": verdict,
            "methods": methods,
        }
