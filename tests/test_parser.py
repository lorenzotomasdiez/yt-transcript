"""Tests for yt_transcript.parser."""

import unittest

from yt_transcript.exceptions import InvalidVideoError
from yt_transcript.parser import extract_video_id, is_valid_video_id


class TestParser(unittest.TestCase):
    def test_is_valid_video_id(self):
        self.assertTrue(is_valid_video_id("dQw4w9WgXcQ"))
        self.assertTrue(is_valid_video_id("abcdefghijk"))

    def test_is_invalid_video_id(self):
        self.assertFalse(is_valid_video_id("short"))
        self.assertFalse(is_valid_video_id("waytoolongvideoid"))
        self.assertFalse(is_valid_video_id("has spaces"))
        self.assertFalse(is_valid_video_id("invalid-chars!"))
        self.assertFalse(is_valid_video_id(""))

    def test_extract_raw_video_id(self):
        self.assertEqual(extract_video_id("dQw4w9WgXcQ"), "dQw4w9WgXcQ")

    def test_extract_from_watch_url(self):
        self.assertEqual(
            extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
            "dQw4w9WgXcQ",
        )

    def test_extract_from_short_url(self):
        self.assertEqual(
            extract_video_id("https://youtu.be/dQw4w9WgXcQ"),
            "dQw4w9WgXcQ",
        )

    def test_extract_from_embed_url(self):
        self.assertEqual(
            extract_video_id("https://www.youtube.com/embed/dQw4w9WgXcQ"),
            "dQw4w9WgXcQ",
        )

    def test_extract_from_shorts_url(self):
        self.assertEqual(
            extract_video_id("https://youtube.com/shorts/dQw4w9WgXcQ"),
            "dQw4w9WgXcQ",
        )

    def test_extract_with_extra_query_params(self):
        self.assertEqual(
            extract_video_id(
                "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=42s&feature=share"
            ),
            "dQw4w9WgXcQ",
        )

    def test_extract_rejects_invalid_url(self):
        with self.assertRaises(InvalidVideoError):
            extract_video_id("https://example.com/watch?v=bad")

    def test_extract_rejects_empty(self):
        with self.assertRaises(InvalidVideoError):
            extract_video_id("")


if __name__ == "__main__":
    unittest.main()
