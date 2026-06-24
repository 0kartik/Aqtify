"""
Video support for PQ-SMAP.

True LSB watermarking of a video's pixel stream doesn't survive the
re-encoding that happens on almost every platform a video gets uploaded
to, so instead of pretending otherwise this module:

  1. Samples frames at 1fps via ffmpeg and hashes each one, combining them
     into a single `video_hash` that is what actually gets signed. This is
     more sensitive to tampering (frame insertion/deletion/edits) than
     hashing the raw container bytes, which changes on every re-encode
     regardless of content.
  2. Extracts the first frame and LSB-watermarks *that* as a standalone
     "keyframe certificate" image (same mechanism as photo watermarking),
     which can be checked against the registry independently of the video
     container.

Registering a video therefore returns both a `video_hash` (signed) and a
watermarked keyframe PNG -- there is no watermark embedded in the video
file itself. See README for the honest limitations here.
"""

import hashlib
import os
import shutil
import subprocess
import tempfile

from PIL import Image

FRAME_SAMPLE_FPS = 1


class VideoProcessor:

    def _ffmpeg_available(self):
        return shutil.which("ffmpeg") is not None

    def extract_sample_frames(self, video_path, out_dir):
        if not self._ffmpeg_available():
            raise RuntimeError("ffmpeg is required for video processing but was not found on PATH.")

        pattern = os.path.join(out_dir, "frame_%05d.png")
        cmd = [
            "ffmpeg", "-y", "-i", video_path,
            "-vf", f"fps={FRAME_SAMPLE_FPS}",
            "-frames:v", "300",  # safety cap
            pattern,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg frame extraction failed: {result.stderr[-500:]}")

        frames = sorted(
            os.path.join(out_dir, f) for f in os.listdir(out_dir) if f.endswith(".png")
        )
        if not frames:
            raise RuntimeError("No frames extracted -- is this a valid video file?")
        return frames

    def compute_video_hash(self, video_path):
        with tempfile.TemporaryDirectory() as tmp:
            frames = self.extract_sample_frames(video_path, tmp)

            hasher = hashlib.sha256()
            for frame_path in frames:
                with open(frame_path, "rb") as f:
                    hasher.update(hashlib.sha256(f.read()).digest())

            first_frame_copy = os.path.join(tempfile.gettempdir(), f"_pqsmap_first_{os.getpid()}.png")
            shutil.copy(frames[0], first_frame_copy)

            return hasher.hexdigest(), first_frame_copy, len(frames)

    def get_duration_seconds(self, video_path):
        if not shutil.which("ffprobe"):
            return None
        cmd = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", video_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        try:
            return round(float(result.stdout.strip()), 2)
        except (ValueError, AttributeError):
            return None
