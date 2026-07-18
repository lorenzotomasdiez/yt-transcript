"""Tests for yt_transcript.config."""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from yt_transcript.config import Config
from yt_transcript.exceptions import ConfigNotFoundError


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.config_path = Path(self.tmpdir.name) / "config.json"
        self.config = Config(path=self.config_path)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_exists_returns_false_when_missing(self):
        self.assertFalse(self.config.exists())

    def test_exists_returns_true_when_present(self):
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config_path.write_text('{"api_key": "secret"}')
        self.assertTrue(self.config.exists())

    def test_load_raises_when_missing(self):
        with self.assertRaises(ConfigNotFoundError):
            self.config.load()

    def test_load_returns_stored_config(self):
        self.config.setup(api_key="secret")
        data = self.config.load()
        self.assertEqual(data["api_key"], "secret")

    def test_setup_writes_api_key(self):
        self.config.setup(api_key="my-key")
        self.assertTrue(self.config.exists())
        self.assertEqual(self.config.get_api_key(), "my-key")
        raw = json.loads(self.config_path.read_text())
        self.assertEqual(raw["api_key"], "my-key")

    def test_setup_prompts_when_no_key_given(self):
        with patch("yt_transcript.config.getpass", return_value="prompted-key"):
            self.config.setup()
        self.assertEqual(self.config.get_api_key(), "prompted-key")

    def test_setup_rejects_empty_key(self):
        with self.assertRaises(ValueError):
            self.config.setup(api_key="")
        with self.assertRaises(ValueError):
            self.config.setup(api_key="   ")

    def test_get_api_key_returns_none_when_missing(self):
        self.assertIsNone(self.config.get_api_key())

    def test_default_path_uses_xdg_config_home(self):
        with patch.dict(os.environ, {"XDG_CONFIG_HOME": "/tmp/xdg"}):
            cfg = Config()
            self.assertEqual(
                cfg.path,
                Path("/tmp/xdg/yt-transcript/config.json"),
            )

    def test_default_path_falls_back_to_home(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch("yt_transcript.config.Path.home", return_value=Path("/home/user")):
                cfg = Config()
                self.assertEqual(
                    cfg.path,
                    Path("/home/user/.config/yt-transcript/config.json"),
                )


if __name__ == "__main__":
    unittest.main()
