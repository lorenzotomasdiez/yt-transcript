# yt-transcript

[![CI](https://github.com/lorenzotomasdiez/yt-transcript/actions/workflows/ci.yml/badge.svg)](https://github.com/lorenzotomasdiez/yt-transcript/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![No dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)](https://github.com/lorenzotomasdiez/yt-transcript)

Headless CLI tool to fetch transcripts and automatic captions from YouTube videos using **your own YouTube Data API key**. Built with zero external dependencies and a full test suite.

## Install

Recommended (works out of the box on macOS and Linux, including distros where the system Python is "externally managed" per PEP 668, such as Homebrew Python or recent Debian/Ubuntu):

```bash
pipx install git+https://github.com/lorenzotomasdiez/yt-transcript.git
```

`pipx` installs the CLI into its own isolated environment and puts `yt-transcript` on your `PATH`, without touching your system Python packages.
Install `pipx` first if you don't have it: `brew install pipx` (macOS) or `python3 -m pip install --user pipx` (Linux), then `pipx ensurepath`.

Alternatively, with plain `pip`:

```bash
pip install git+https://github.com/lorenzotomasdiez/yt-transcript.git
```

If this fails with an "externally-managed-environment" error, either use `pipx` above, or install inside a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install git+https://github.com/lorenzotomasdiez/yt-transcript.git
```

## Uninstall

If you installed with `pipx`:

```bash
pipx uninstall yt-transcript
```

If you installed with plain `pip`:

```bash
pip uninstall yt-transcript
```

If you installed inside a virtual environment, deleting the `.venv` directory is enough.

## Requirements

- Python 3.9+
- A [YouTube Data API v3](https://developers.google.com/youtube/registering_an_application) key

## Setup

Before fetching transcripts, configure your API key:

```bash
# Interactive prompt (secure, hidden input)
yt-transcript setup

# Or pass it directly
yt-transcript setup --api-key YOUR_API_KEY
```

The key is stored locally at `~/.config/yt-transcript/config.json`.

If you skip this step, every transcript command will exit with a clear error until you either run `setup` or pass `--ext-api`.

## Usage

```bash
# Fetch the default transcript (text output)
yt-transcript "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# List available caption languages
yt-transcript "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --list-languages

# Choose a language
yt-transcript "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --lang en

# Translate automatic captions
yt-transcript "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --translate es

# Output formats: text (default), json, srt, vtt
yt-transcript "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --format srt --output captions.srt

# Use a different API key for a single call
yt-transcript "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --ext-api OTHER_KEY
```

## How it works

This tool combines two YouTube APIs:

- **YouTube Data API v3** (your API key) — validates the video and lists available caption tracks.
- **YouTube Innertube API** (no key needed) — fetches the actual transcript text using signed caption URLs, the same mechanism the web player uses.

The Data API alone cannot download caption text (the `captions/download` endpoint requires OAuth 2.0), and the legacy `timedtext` endpoint no longer works reliably. Innertube is the practical, headless alternative.

## Development

```bash
# Run the test suite
make test

# Or directly
python3 -m unittest discover -s tests -v
```

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our development process and how to submit pull requests.

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). Please be respectful to everyone in the community.

## Security

See [SECURITY.md](SECURITY.md) for reporting vulnerabilities.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for release history.

## License

[MIT](LICENSE)
