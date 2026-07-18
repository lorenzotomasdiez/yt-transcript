"""Domain exceptions for yt-transcript."""


class YTTranscriptError(Exception):
    """Base exception for all yt-transcript errors."""


class ConfigNotFoundError(YTTranscriptError):
    """Raised when the API key has not been configured."""


class InvalidVideoError(YTTranscriptError):
    """Raised when a YouTube URL or video id is invalid."""


class APIError(YTTranscriptError):
    """Raised when the YouTube Data API returns an error."""

    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.status_code = status_code

    def __str__(self):
        if self.status_code:
            return f"[HTTP {self.status_code}] {self.args[0]}"
        return self.args[0]


class TranscriptsDisabled(YTTranscriptError):
    """Raised when a video has no transcript data available."""

    def __init__(self, video_id):
        super().__init__(f"Transcripts are disabled for video '{video_id}'.")


class LanguageUnavailable(YTTranscriptError):
    """Raised when the requested language is not available."""

    def __init__(self, video_id, language):
        super().__init__(
            f"Language '{language}' is not available for video '{video_id}'."
        )


class VideoUnavailable(YTTranscriptError):
    """Raised when the video is not found or unavailable."""

    def __init__(self, video_id):
        super().__init__(f"Video '{video_id}' is unavailable or not found.")
