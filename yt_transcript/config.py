"""Persistent configuration for yt-transcript."""

import json
import os
from getpass import getpass
from pathlib import Path

from yt_transcript.exceptions import ConfigNotFoundError


class Config:
    """Manages the local configuration file for the YouTube API key."""

    def __init__(self, path=None):
        if path is not None:
            self.path = Path(path)
        else:
            self.path = self._default_path()

    @staticmethod
    def _default_path():
        """Return the default configuration file path."""
        config_home = os.environ.get("XDG_CONFIG_HOME")
        if config_home:
            base = Path(config_home)
        else:
            base = Path.home() / ".config"
        return base / "yt-transcript" / "config.json"

    def exists(self):
        """Return True if the configuration file exists."""
        return self.path.exists()

    def load(self):
        """Load and return the configuration as a dict."""
        if not self.exists():
            raise ConfigNotFoundError(
                "API key not configured. Run 'yt-transcript setup' first or use '--ext-api'."
            )
        return json.loads(self.path.read_text(encoding="utf-8"))

    def get_api_key(self):
        """Return the stored API key or None."""
        if not self.exists():
            return None
        return self.load().get("api_key")

    def setup(self, api_key=None):
        """Save the API key to the configuration file.

        If no key is provided, prompt the user securely.
        """
        if api_key is None:
            api_key = getpass("Enter your YouTube Data API key: ")

        api_key = api_key.strip()
        if not api_key:
            raise ValueError("API key cannot be empty.")

        self.path.parent.mkdir(parents=True, exist_ok=True)
        config = {"api_key": api_key}
        self.path.write_text(json.dumps(config, indent=2), encoding="utf-8")
