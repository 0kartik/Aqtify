import os
import mimetypes


class MediaProcessor:

    IMAGE_TYPES = {".jpg", ".jpeg", ".png", ".bmp"}
    VIDEO_TYPES = {".mp4", ".avi", ".mov"}
    AUDIO_TYPES = {".wav", ".mp3"}

    def file_exists(self, file_path):
        return os.path.isfile(file_path)

    def get_extension(self, file_path):
        return os.path.splitext(file_path)[1].lower()

    def get_media_type(self, file_path):
        extension = self.get_extension(file_path)

        if extension in self.IMAGE_TYPES:
            return "image"
        if extension in self.VIDEO_TYPES:
            return "video"
        if extension in self.AUDIO_TYPES:
            return "audio"
        return "unknown"

    def get_file_size_mb(self, file_path):
        size_bytes = os.path.getsize(file_path)
        return round(size_bytes / (1024 * 1024), 2)

    def get_mime_type(self, file_path):
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type

    def validate_file(self, file_path):
        if not self.file_exists(file_path):
            return False, "File does not exist"

        media_type = self.get_media_type(file_path)

        if media_type == "unknown":
            return False, "Unsupported media format"

        return True, media_type

    def get_metadata(self, file_path):
        return {
            "file_name": os.path.basename(file_path),
            "media_type": self.get_media_type(file_path),
            "mime_type": self.get_mime_type(file_path),
            "size_mb": self.get_file_size_mb(file_path),
        }
