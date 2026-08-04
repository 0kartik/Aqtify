"""
AI-generated / synthetic media detector.

IMAGES: a single pretrained classifier (prithivMLmods/Deep-Fake-Detector-v2-Model,
ViT/transformer). An earlier version of this module ran a 2-model ensemble
(this ViT model + Organika/sdxl-detector, a Swin Transformer). That
pairing was dropped after direct testing showed Organika inverting on
real test cases -- scoring a genuine phone photo at 100% AI-probability
and an actual Gemini-generated image at 6.4%, actively pulling the
ensemble average in the wrong direction rather than correcting the ViT
model's own blind spots. No free, self-hostable model tested so far
generalizes reliably across camera types and generators (a known,
published, industry-wide limitation -- even paid commercial detectors
report meaningfully lower accuracy on heavily-processed real photography).
Given that, a single reasonably-behaved model plus a wide human-review
band is more honest and more reliable than averaging in a second model
that doesn't consistently agree with reality.

AUDIO: Mrkomiljon/voiceGUARD, a Wav2Vec2-based synthetic-speech / voice-
clone classifier.

VIDEO: no dedicated video model (self-hosting one is heavy and slow on
CPU-only hardware). Instead, sample frames are extracted via the existing
VideoProcessor and screened through the same image ensemble; the video's
score is the max across sampled frames, since a single AI-generated or
manipulated frame is enough to be meaningful evidence.

All models run fully offline once cached (see download_model.py). If a
model is missing, it's dropped from the ensemble rather than crashing --
but analyze_media() reports exactly which models actually voted, so the
caller (and the registration gate) can decide whether that's still enough
signal to trust.
"""

import os
import logging

logger = logging.getLogger("aqtify.deepfake_detector")

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

from PIL import Image

# Fine-tuned locally on Parveshiiii/AI-vs-Real (13,999 images) via Colab
# T4 GPU, classification head only (1,538 trainable params). Verified
# 89.0% accuracy on held-out test data after save/reload, matching the
# 87.7% seen during training -- confirmed not degraded by the save step.
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_MODEL_NAMES = [
    os.path.join(_THIS_DIR, "models", "aqtify_finetuned_model"),
]

_IMAGE_PROCESSOR_OVERRIDES = {}
AUDIO_MODEL_NAME = "Mrkomiljon/voiceGUARD"

_image_models = {}   # name -> (model, processor)
_image_load_errors = {}  # name -> error string
_audio_model = None
_audio_processor = None
_audio_load_error = None


# ------------------------------------------------------------------
# Model loading (lazy, once per process)
# ------------------------------------------------------------------

def _load_image_models():
    if _image_models or _image_load_errors:
        return  # already attempted

    from transformers import AutoImageProcessor, AutoModelForImageClassification

    for name in IMAGE_MODEL_NAMES:
        try:
            model = AutoModelForImageClassification.from_pretrained(name)
            processor_source = _IMAGE_PROCESSOR_OVERRIDES.get(name, name)
            processor = AutoImageProcessor.from_pretrained(processor_source)
            model.eval()
            _image_models[name] = (model, processor)
            logger.info("Loaded image AI-detection model: %s", name)
        except Exception as exc:
            _image_load_errors[name] = str(exc)
            logger.error(
                "FAILED to load image AI-detection model %s: %s. "
                "This model will be dropped from the ensemble.",
                name, exc,
            )


def _load_audio_model():
    global _audio_model, _audio_processor, _audio_load_error

    if _audio_model is not None or _audio_load_error is not None:
        return

    try:
        from transformers import Wav2Vec2ForSequenceClassification, Wav2Vec2Processor

        _audio_model = Wav2Vec2ForSequenceClassification.from_pretrained(AUDIO_MODEL_NAME)
        _audio_processor = Wav2Vec2Processor.from_pretrained(AUDIO_MODEL_NAME)
        _audio_model.eval()
        logger.info("Loaded audio AI-detection model: %s", AUDIO_MODEL_NAME)
    except Exception as exc:
        _audio_load_error = str(exc)
        logger.error(
            "FAILED to load audio AI-detection model %s: %s. "
            "Audio screening will be UNAVAILABLE until this is fixed.",
            AUDIO_MODEL_NAME, exc,
        )


# ------------------------------------------------------------------
# Per-model inference helpers
# ------------------------------------------------------------------

def _find_ai_label_index(id2label):
    """Different model authors used different label names -- find whichever
    one clearly means 'AI-generated / fake' rather than hardcoding a string."""
    fake_terms = ("deepfake", "fake", "ai", "synthetic", "generated", "artificial")
    for idx, label in id2label.items():
        low = str(label).lower()
        if any(term in low for term in fake_terms) and "real" not in low:
            return idx
    # Fallback: assume index 1 is "fake" (common convention), 0 is "real"
    return 1


def _score_image_with_model(name, model, processor, pil_image):
    import torch

    inputs = processor(images=pil_image, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)[0]

    ai_idx = _find_ai_label_index(model.config.id2label)
    return float(probs[ai_idx]) * 100


def _run_image_ensemble(pil_image):
    """Returns (average_ai_probability, per_model_scores dict, models_used list)."""

    _load_image_models()

    scores = {}
    for name, (model, processor) in _image_models.items():
        try:
            scores[name] = round(_score_image_with_model(name, model, processor, pil_image), 1)
        except Exception as exc:
            logger.error("Image model %s failed during inference: %s", name, exc)

    if not scores:
        return None, {}, []

    avg = round(sum(scores.values()) / len(scores), 1)
    return avg, scores, list(scores.keys())


def _score_audio(file_path):
    _load_audio_model()

    if _audio_model is None:
        return None, _audio_load_error

    import torch
    import torchaudio

    waveform, sample_rate = torchaudio.load(file_path)
    if waveform.shape[0] > 1:
        waveform = waveform.mean(dim=0, keepdim=True)  # downmix to mono
    if sample_rate != 16000:
        resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)
        waveform = resampler(waveform)

    inputs = _audio_processor(
        waveform.squeeze().numpy(), sampling_rate=16000, return_tensors="pt", padding=True
    )
    with torch.no_grad():
        logits = _audio_model(**inputs).logits
        probs = torch.nn.functional.softmax(logits, dim=-1)[0]

    ai_idx = _find_ai_label_index(_audio_model.config.id2label)
    return round(float(probs[ai_idx]) * 100, 1), None


# ------------------------------------------------------------------
# Public entrypoint
# ------------------------------------------------------------------

class DeepfakeDetector:

    def analyze_media(self, file_path, media_type="image", video_processor=None):
        """
        media_type: "image" | "audio" | "video"
        video_processor: required for media_type="video" -- an instance
        exposing extract_sample_frames(video_path, out_dir), reused from
        the existing VideoProcessor to avoid a second ffmpeg integration.
        """

        if media_type == "image":
            return self._analyze_image(file_path)
        if media_type == "audio":
            return self._analyze_audio(file_path)
        if media_type == "video":
            return self._analyze_video(file_path, video_processor)

        return {
            "supported": False,
            "error": f"Unknown media_type: {media_type}",
            "ai_probability": None,
            "verdict": "UNKNOWN",
        }

    def _verdict_from_probability(self, ai_probability):
        if ai_probability > 70:
            return "LIKELY AI-GENERATED"
        if ai_probability > 40:
            return "SUSPICIOUS"
        return "LIKELY AUTHENTIC"

    def _analyze_image(self, file_path):
        try:
            pil_image = Image.open(file_path).convert("RGB")
        except Exception as exc:
            return {
                "supported": False,
                "error": f"Could not open file: {exc}",
                "ai_probability": None,
                "verdict": "UNKNOWN",
            }

        avg, per_model, models_used = _run_image_ensemble(pil_image)

        if avg is None:
            return {
                "supported": False,
                "error": "No image AI-detection models could be loaded.",
                "ai_probability": None,
                "verdict": "UNKNOWN",
            }

        return {
            "supported": True,
            "media_type": "image",
            "ai_probability": avg,
            "verdict": self._verdict_from_probability(avg),
            "ensemble": per_model,
            "models_used": models_used,
            "models_expected": len(IMAGE_MODEL_NAMES),
        }

    def _analyze_audio(self, file_path):
        score, error = _score_audio(file_path)

        if score is None:
            return {
                "supported": False,
                "error": f"Audio AI-detection model unavailable: {error}",
                "ai_probability": None,
                "verdict": "UNKNOWN",
            }

        return {
            "supported": True,
            "media_type": "audio",
            "ai_probability": score,
            "verdict": self._verdict_from_probability(score),
            "model_name": AUDIO_MODEL_NAME,
        }

    def _analyze_video(self, file_path, video_processor):
        if video_processor is None:
            return {
                "supported": False,
                "error": "No VideoProcessor supplied for keyframe extraction.",
                "ai_probability": None,
                "verdict": "UNKNOWN",
            }

        import tempfile

        try:
            with tempfile.TemporaryDirectory() as tmp_dir:
                frame_paths = video_processor.extract_sample_frames(file_path, tmp_dir)

                frame_scores = []
                per_frame_detail = []
                for frame_path in frame_paths:
                    try:
                        pil_frame = Image.open(frame_path).convert("RGB")
                        avg, per_model, models_used = _run_image_ensemble(pil_frame)
                        if avg is not None:
                            frame_scores.append(avg)
                            per_frame_detail.append(round(avg, 1))
                    except Exception as exc:
                        logger.error("Failed scoring video frame %s: %s", frame_path, exc)

        except Exception as exc:
            return {
                "supported": False,
                "error": f"Frame extraction failed: {exc}",
                "ai_probability": None,
                "verdict": "UNKNOWN",
            }

        if not frame_scores:
            return {
                "supported": False,
                "error": "No frames could be scored (model unavailable or extraction produced nothing).",
                "ai_probability": None,
                "verdict": "UNKNOWN",
            }

        # Max across frames: one clearly AI/manipulated frame is meaningful
        # evidence even if most of the video is untouched.
        worst = round(max(frame_scores), 1)
        avg_all = round(sum(frame_scores) / len(frame_scores), 1)

        return {
            "supported": True,
            "media_type": "video",
            "ai_probability": worst,
            "verdict": self._verdict_from_probability(worst),
            "frames_sampled": len(frame_scores),
            "frame_scores": per_frame_detail,
            "average_across_frames": avg_all,
            "note": "Score is the maximum across sampled frames (1fps), not an average, "
                    "since a single manipulated frame is meaningful evidence.",
        }