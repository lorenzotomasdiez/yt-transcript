"""Tests for yt_transcript.formatter."""

import json
import unittest

from yt_transcript.formatter import format_transcript


SAMPLE_SEGMENTS = [
    {"text": "Hello world", "start": 0.5, "duration": 2.1},
    {"text": "Second line", "start": 3.0, "duration": 1.5},
]


class TestFormatter(unittest.TestCase):
    def test_format_text(self):
        output = format_transcript(SAMPLE_SEGMENTS, "text")
        self.assertEqual(output, "Hello world\nSecond line")

    def test_format_json(self):
        output = format_transcript(SAMPLE_SEGMENTS, "json")
        data = json.loads(output)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["text"], "Hello world")

    def test_format_srt(self):
        output = format_transcript(SAMPLE_SEGMENTS, "srt")
        lines = output.split("\n")
        self.assertEqual(lines[0], "1")
        self.assertEqual(lines[1], "00:00:00,500 --> 00:00:02,600")
        self.assertEqual(lines[2], "Hello world")
        self.assertEqual(lines[4], "2")

    def test_format_vtt(self):
        output = format_transcript(SAMPLE_SEGMENTS, "vtt")
        self.assertTrue(output.startswith("WEBVTT\n\n"))
        self.assertIn("00:00:00.500 --> 00:00:02.600", output)
        self.assertIn("Hello world", output)

    def test_invalid_format_raises(self):
        with self.assertRaises(ValueError):
            format_transcript(SAMPLE_SEGMENTS, "yaml")


if __name__ == "__main__":
    unittest.main()
