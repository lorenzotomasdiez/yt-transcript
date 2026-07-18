"""Tests for yt_transcript.innertube."""

import json
import unittest
from io import BytesIO
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError

from yt_transcript.exceptions import (
    APIError,
    InvalidVideoError,
    LanguageUnavailable,
    TranscriptsDisabled,
    VideoUnavailable,
)
from yt_transcript.innertube import INNERTUBE_API_KEY, InnertubeClient


SAMPLE_PLAYER_RESPONSE = {
    "playabilityStatus": {"status": "OK"},
    "captions": {
        "playerCaptionsTracklistRenderer": {
            "captionTracks": [
                {
                    "baseUrl": "https://www.youtube.com/api/timedtext?v=abc123&lang=en&fmt=srv3",
                    "languageCode": "en",
                    "name": {"runs": [{"text": "English"}]},
                    "kind": "asr",
                },
                {
                    "baseUrl": "https://www.youtube.com/api/timedtext?v=abc123&lang=es&fmt=srv3",
                    "languageCode": "es",
                    "name": {"runs": [{"text": "Español"}]},
                },
            ]
        }
    },
}

SAMPLE_PLAYER_RESPONSE_NO_CAPTIONS = {
    "playabilityStatus": {"status": "OK"},
}

SAMPLE_PLAYER_RESPONSE_UNPLAYABLE = {
    "playabilityStatus": {
        "status": "ERROR",
        "reason": "This video is unavailable",
    },
}

SAMPLE_TRANSCRIPT_XML = b"""<?xml version="1.0" encoding="utf-8"?>
<transcript>
    <text start="0.5" dur="2.1">Hello world</text>
    <text start="3.0" dur="1.5">Second line</text>
</transcript>
"""


class TestInnertubeClient(unittest.TestCase):
    def setUp(self):
        self.client = InnertubeClient(timeout=10)

    def _mock_response(self, body, status=200):
        resp = BytesIO(body if isinstance(body, bytes) else body.encode())
        resp.status = status
        resp.headers = {"Content-Type": "application/json"}
        return resp

    def _http_error(self, code, body=b"{}"):
        err = HTTPError(
            url="https://example.com",
            code=code,
            msg="Error",
            hdrs={},
            fp=BytesIO(body),
        )
        self.addCleanup(err.close)
        return err

    @patch("yt_transcript.innertube.urlopen")
    def test_fetches_tracks_via_innertube(self, mock_urlopen):
        mock_urlopen.return_value = self._mock_response(
            json.dumps(SAMPLE_PLAYER_RESPONSE).encode()
        )

        tracks = self.client.get_caption_tracks("abc123")

        self.assertEqual(len(tracks), 2)
        self.assertEqual(tracks[0]["language_code"], "en")
        self.assertTrue(tracks[0]["is_auto"])
        self.assertEqual(tracks[1]["language_code"], "es")
        self.assertFalse(tracks[1]["is_auto"])

        # Verify the sole request went straight to the Innertube player API,
        # skipping the watch page HTML fetch entirely.
        self.assertEqual(mock_urlopen.call_count, 1)
        url = mock_urlopen.call_args[0][0].full_url
        self.assertIn(f"key={INNERTUBE_API_KEY}", url)

    @patch("yt_transcript.innertube.urlopen")
    def test_raises_when_no_captions(self, mock_urlopen):
        mock_urlopen.return_value = self._mock_response(
            json.dumps(SAMPLE_PLAYER_RESPONSE_NO_CAPTIONS).encode()
        )
        with self.assertRaises(TranscriptsDisabled):
            self.client.get_caption_tracks("abc123")

    @patch("yt_transcript.innertube.urlopen")
    def test_raises_when_video_unavailable(self, mock_urlopen):
        mock_urlopen.return_value = self._mock_response(
            json.dumps(SAMPLE_PLAYER_RESPONSE_UNPLAYABLE).encode()
        )
        with self.assertRaises(VideoUnavailable):
            self.client.get_caption_tracks("abc123")

    @patch("yt_transcript.innertube.urlopen")
    def test_raises_when_ip_blocked(self, mock_urlopen):
        err = self._http_error(429)
        mock_urlopen.side_effect = err
        with self.assertRaises(APIError):
            self.client.get_caption_tracks("abc123")

    @patch("yt_transcript.innertube.urlopen")
    def test_fetch_transcript_parses_xml(self, mock_urlopen):
        mock_urlopen.return_value = self._mock_response(SAMPLE_TRANSCRIPT_XML)

        segments = self.client.fetch_transcript(
            "https://www.youtube.com/api/timedtext?v=abc123&lang=en"
        )

        self.assertEqual(len(segments), 2)
        self.assertEqual(segments[0]["text"], "Hello world")
        self.assertEqual(segments[0]["start"], 0.5)
        self.assertEqual(segments[0]["duration"], 2.1)

    @patch("yt_transcript.innertube.urlopen")
    def test_fetch_transcript_removes_srv3_format(self, mock_urlopen):
        mock_urlopen.return_value = self._mock_response(SAMPLE_TRANSCRIPT_XML)

        self.client.fetch_transcript(
            "https://www.youtube.com/api/timedtext?v=abc123&lang=en&fmt=srv3"
        )

        url = mock_urlopen.call_args[0][0].full_url
        self.assertNotIn("fmt=srv3", url)


if __name__ == "__main__":
    unittest.main()
