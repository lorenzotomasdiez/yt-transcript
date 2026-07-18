"""Tests for yt_transcript.cli."""

import io
import unittest
from unittest.mock import patch

from yt_transcript.cli import main, parse_args


class TestParseArgs(unittest.TestCase):
    def test_parse_video_only(self):
        args = parse_args(["https://youtu.be/dQw4w9WgXcQ"])
        self.assertEqual(args.video, "https://youtu.be/dQw4w9WgXcQ")
        self.assertFalse(args.list_languages)
        self.assertEqual(args.format, "text")

    def test_parse_setup_command(self):
        args = parse_args(["setup", "--api-key", "secret"])
        self.assertEqual(args.command, "setup")
        self.assertEqual(args.api_key, "secret")

    def test_parse_ext_api(self):
        args = parse_args(["abc123", "--ext-api", "other-key"])
        self.assertEqual(args.ext_api, "other-key")

    def test_parse_format(self):
        args = parse_args(["abc123", "--format", "srt"])
        self.assertEqual(args.format, "srt")

    def test_invalid_format_rejected(self):
        with self.assertRaises(SystemExit):
            parse_args(["abc123", "--format", "bad"])


class TestCLI(unittest.TestCase):
    def setUp(self):
        self.patches = []

    def _patch(self, target):
        p = patch(target)
        self.patches.append(p)
        return p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()

    def test_setup_command_saves_key(self):
        mock_config = self._patch("yt_transcript.cli.Config")
        code = main(["setup", "--api-key", "secret"])
        self.assertEqual(code, 0)
        mock_config.return_value.setup.assert_called_once_with(api_key="secret")

    def test_missing_api_key_rejected(self):
        mock_config = self._patch("yt_transcript.cli.Config")
        mock_config.return_value.exists.return_value = False
        mock_config.return_value.get_api_key.return_value = None

        with patch("sys.stderr", new=io.StringIO()) as stderr:
            code = main(["abc123"])

        self.assertEqual(code, 1)
        self.assertIn("setup", stderr.getvalue())

    def test_list_languages(self):
        mock_config = self._patch("yt_transcript.cli.Config")
        mock_config.return_value.get_api_key.return_value = "stored-key"

        mock_api = self._patch("yt_transcript.cli.YouTubeDataAPI")
        mock_api.return_value.list_captions.return_value = [
            {"language": "en", "name": "English", "is_auto": True},
            {"language": "es", "name": "Español", "is_auto": False},
        ]

        with patch("sys.stdout", new=io.StringIO()) as stdout:
            code = main(["dQw4w9WgXcQ", "--list-languages"])

        self.assertEqual(code, 0)
        output = stdout.getvalue()
        self.assertIn("en", output)
        self.assertIn("Español", output)

    def test_fetch_and_print_text(self):
        mock_config = self._patch("yt_transcript.cli.Config")
        mock_config.return_value.get_api_key.return_value = "stored-key"

        self._patch(
            "yt_transcript.cli.YouTubeDataAPI",
        ).return_value.list_captions.return_value = [
            {"language": "en", "name": "English", "is_auto": True},
        ]

        self._patch(
            "yt_transcript.cli.fetch_transcript",
        ).return_value = [
            {"text": "Hello", "start": 0.0, "duration": 1.0},
        ]

        with patch("sys.stdout", new=io.StringIO()) as stdout:
            code = main(["dQw4w9WgXcQ"])

        self.assertEqual(code, 0)
        self.assertIn("Hello", stdout.getvalue())

    def test_ext_api_overrides_stored_key(self):
        mock_config = self._patch("yt_transcript.cli.Config")
        mock_config.return_value.get_api_key.return_value = "stored-key"

        mock_api = self._patch("yt_transcript.cli.YouTubeDataAPI")
        mock_api.return_value.list_captions.return_value = [
            {"language": "en", "name": "English", "is_auto": True},
        ]

        self._patch(
            "yt_transcript.cli.fetch_transcript",
        ).return_value = [
            {"text": "Hello", "start": 0.0, "duration": 1.0},
        ]

        main(["dQw4w9WgXcQ", "--ext-api", "override-key"])
        mock_api.assert_called_once_with(api_key="override-key", timeout=30)

    def test_invalid_video_error(self):
        mock_config = self._patch("yt_transcript.cli.Config")
        mock_config.return_value.get_api_key.return_value = "stored-key"

        with patch("sys.stderr", new=io.StringIO()) as stderr:
            code = main(["not-a-valid-id"])

        self.assertEqual(code, 1)
        self.assertIn("Invalid", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
