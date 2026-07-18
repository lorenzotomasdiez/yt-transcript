"""Tests for yt_transcript.api."""

import json
import unittest
from io import BytesIO
from unittest.mock import patch
from urllib.error import HTTPError

from yt_transcript.api import YouTubeDataAPI
from yt_transcript.exceptions import APIError, VideoUnavailable


class TestYouTubeDataAPI(unittest.TestCase):
    def setUp(self):
        self.api = YouTubeDataAPI(api_key="test-key", timeout=10)

    def _mock_response(self, body, status=200):
        resp = BytesIO(json.dumps(body).encode())
        resp.status = status
        resp.headers = {"Content-Type": "application/json"}
        return resp

    @patch("yt_transcript.api.urlopen")
    def test_list_captions_parses_tracks(self, mock_urlopen):
        mock_urlopen.return_value = self._mock_response(
            {
                "items": [
                    {
                        "id": "caption1",
                        "snippet": {
                            "language": "en",
                            "name": "English",
                            "videoId": "abc123",
                            "isAutoSynced": True,
                        },
                    },
                    {
                        "id": "caption2",
                        "snippet": {
                            "language": "es",
                            "name": "Español",
                            "videoId": "abc123",
                            "isAutoSynced": False,
                        },
                    },
                ]
            }
        )

        tracks = self.api.list_captions("abc123")
        self.assertEqual(len(tracks), 2)
        self.assertEqual(tracks[0]["language"], "en")
        self.assertTrue(tracks[0]["is_auto"])
        self.assertEqual(tracks[1]["language"], "es")
        self.assertFalse(tracks[1]["is_auto"])

        call = mock_urlopen.call_args
        url = call[0][0].full_url
        self.assertIn("videoId=abc123", url)
        self.assertIn("key=test-key", url)

    @patch("yt_transcript.api.urlopen")
    def test_list_captions_returns_empty_list(self, mock_urlopen):
        mock_urlopen.return_value = self._mock_response({"items": []})
        tracks = self.api.list_captions("abc123")
        self.assertEqual(tracks, [])

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

    @patch("yt_transcript.api.urlopen")
    def test_list_captions_raises_api_error(self, mock_urlopen):
        err = self._http_error(
            400,
            b'{"error":{"message":"Invalid API key"}}',
        )
        mock_urlopen.side_effect = err

        with self.assertRaises(APIError) as ctx:
            self.api.list_captions("abc123")
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("Invalid API key", str(ctx.exception))

    @patch("yt_transcript.api.urlopen")
    def test_list_captions_raises_video_unavailable_for_404(self, mock_urlopen):
        err = self._http_error(404)
        mock_urlopen.side_effect = err

        with self.assertRaises(VideoUnavailable):
            self.api.list_captions("abc123")


if __name__ == "__main__":
    unittest.main()
