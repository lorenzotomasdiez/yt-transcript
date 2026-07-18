"""Tests for yt_transcript.transcript."""

import unittest
from unittest.mock import patch

from yt_transcript.exceptions import LanguageUnavailable, TranscriptsDisabled
from yt_transcript.transcript import fetch_transcript


SAMPLE_TRACKS = [
    {
        "language_code": "en",
        "language": "English",
        "base_url": "https://www.youtube.com/api/timedtext?v=abc123&lang=en",
        "is_auto": True,
    },
    {
        "language_code": "es",
        "language": "Español",
        "base_url": "https://www.youtube.com/api/timedtext?v=abc123&lang=es",
        "is_auto": False,
    },
]

SAMPLE_SEGMENTS = [
    {"text": "Hello world", "start": 0.5, "duration": 2.1},
    {"text": "Second line", "start": 3.0, "duration": 1.5},
]


class TestFetchTranscript(unittest.TestCase):
    @patch("yt_transcript.transcript.InnertubeClient")
    def test_fetch_uses_first_available_language(self, mock_client_cls):
        mock_client = mock_client_cls.return_value
        mock_client.get_caption_tracks.return_value = SAMPLE_TRACKS
        mock_client.fetch_transcript.return_value = SAMPLE_SEGMENTS

        segments = fetch_transcript("abc123")

        self.assertEqual(segments, SAMPLE_SEGMENTS)
        mock_client.fetch_transcript.assert_called_once_with(SAMPLE_TRACKS[0]["base_url"])

    @patch("yt_transcript.transcript.InnertubeClient")
    def test_fetch_with_specific_language(self, mock_client_cls):
        mock_client = mock_client_cls.return_value
        mock_client.get_caption_tracks.return_value = SAMPLE_TRACKS
        mock_client.fetch_transcript.return_value = SAMPLE_SEGMENTS

        segments = fetch_transcript("abc123", language="es")

        self.assertEqual(segments, SAMPLE_SEGMENTS)
        mock_client.fetch_transcript.assert_called_once_with(SAMPLE_TRACKS[1]["base_url"])

    @patch("yt_transcript.transcript.InnertubeClient")
    def test_fetch_with_translation(self, mock_client_cls):
        mock_client = mock_client_cls.return_value
        mock_client.get_caption_tracks.return_value = SAMPLE_TRACKS
        mock_client.fetch_transcript.return_value = SAMPLE_SEGMENTS

        fetch_transcript("abc123", language="en", translate="fr")

        called_url = mock_client.fetch_transcript.call_args[0][0]
        self.assertIn("tlang=fr", called_url)

    @patch("yt_transcript.transcript.InnertubeClient")
    def test_raises_when_no_tracks(self, mock_client_cls):
        mock_client = mock_client_cls.return_value
        mock_client.get_caption_tracks.return_value = []

        with self.assertRaises(TranscriptsDisabled):
            fetch_transcript("abc123")

    @patch("yt_transcript.transcript.InnertubeClient")
    def test_raises_when_language_unavailable(self, mock_client_cls):
        mock_client = mock_client_cls.return_value
        mock_client.get_caption_tracks.return_value = SAMPLE_TRACKS

        with self.assertRaises(LanguageUnavailable):
            fetch_transcript("abc123", language="zz")

    @patch("yt_transcript.transcript.InnertubeClient")
    def test_prefers_manual_captions(self, mock_client_cls):
        mock_client = mock_client_cls.return_value
        tracks = [
            {
                "language_code": "en",
                "language": "English (auto)",
                "base_url": "https://example.com/auto",
                "is_auto": True,
            },
            {
                "language_code": "en",
                "language": "English",
                "base_url": "https://example.com/manual",
                "is_auto": False,
            },
        ]
        mock_client.get_caption_tracks.return_value = tracks
        mock_client.fetch_transcript.return_value = SAMPLE_SEGMENTS

        fetch_transcript("abc123", language="en")

        mock_client.fetch_transcript.assert_called_once_with("https://example.com/manual")


if __name__ == "__main__":
    unittest.main()
