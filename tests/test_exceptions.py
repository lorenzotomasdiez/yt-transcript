"""Tests for yt_transcript.exceptions."""

import unittest

from yt_transcript.exceptions import (
    APIError,
    ConfigNotFoundError,
    InvalidVideoError,
    LanguageUnavailable,
    TranscriptsDisabled,
    VideoUnavailable,
    YTTranscriptError,
)


class TestExceptions(unittest.TestCase):
    def test_base_exception(self):
        err = YTTranscriptError("base error")
        self.assertIsInstance(err, Exception)
        self.assertEqual(str(err), "base error")

    def test_config_not_found_error(self):
        err = ConfigNotFoundError("missing")
        self.assertIsInstance(err, YTTranscriptError)
        self.assertEqual(str(err), "missing")

    def test_invalid_video_error(self):
        err = InvalidVideoError("bad id")
        self.assertIsInstance(err, YTTranscriptError)
        self.assertEqual(str(err), "bad id")

    def test_api_error(self):
        err = APIError("quota exceeded", status_code=403)
        self.assertIsInstance(err, YTTranscriptError)
        self.assertEqual(err.status_code, 403)
        self.assertIn("quota exceeded", str(err))

    def test_transcripts_disabled(self):
        err = TranscriptsDisabled("abc123")
        self.assertIsInstance(err, YTTranscriptError)
        self.assertIn("abc123", str(err))

    def test_language_unavailable(self):
        err = LanguageUnavailable("abc123", "zz")
        self.assertIsInstance(err, YTTranscriptError)
        self.assertIn("abc123", str(err))
        self.assertIn("zz", str(err))

    def test_video_unavailable(self):
        err = VideoUnavailable("abc123")
        self.assertIsInstance(err, YTTranscriptError)
        self.assertIn("abc123", str(err))


if __name__ == "__main__":
    unittest.main()
