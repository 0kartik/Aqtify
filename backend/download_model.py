"""
Downloads and caches every AI-detection model used by Aqtify:

  Images (single model -- see deepfake_detector.py docstring for why the
  2-model ensemble was dropped):
    1. prithivMLmods/Deep-Fake-Detector-v2-Model   -- ViT (transformer)

  Audio (synthetic speech / voice-clone detection):
    2. Mrkomiljon/voiceGUARD                       -- Wav2Vec2

  Video reuses the image model on sampled keyframes -- no separate
  video model to download.

Run this ONCE with internet on. After that everything runs offline.
"""

import os

os.environ.pop("HF_HUB_OFFLINE", None)
os.environ.pop("TRANSFORMERS_OFFLINE", None)

from transformers import (
    AutoImageProcessor,
    AutoModelForImageClassification,
    Wav2Vec2ForSequenceClassification,
    Wav2Vec2Processor,
)

IMAGE_MODELS = [
    "prithivMLmods/Deep-Fake-Detector-v2-Model",
]

_IMAGE_PROCESSOR_OVERRIDES = {}

AUDIO_MODEL = "Mrkomiljon/voiceGUARD"


def download_image_models():
    for name in IMAGE_MODELS:
        print(f"\nDownloading image model: {name}")
        model = AutoModelForImageClassification.from_pretrained(name)
        processor_source = _IMAGE_PROCESSOR_OVERRIDES.get(name, name)
        AutoImageProcessor.from_pretrained(processor_source)
        print(f"  labels: {model.config.id2label}")


def download_audio_model():
    print(f"\nDownloading audio model: {AUDIO_MODEL}")
    Wav2Vec2ForSequenceClassification.from_pretrained(AUDIO_MODEL)
    Wav2Vec2Processor.from_pretrained(AUDIO_MODEL)
    print("  audio model cached.")


if __name__ == "__main__":
    download_image_models()
    download_audio_model()
    print("\nAll models downloaded and cached locally (~/.cache/huggingface/hub).")
    print("Video screening reuses the image ensemble on sampled keyframes -- nothing extra to download.")