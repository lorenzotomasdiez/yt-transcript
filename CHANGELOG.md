# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- Replaced broken legacy `timedtext` endpoint with YouTube Innertube API for reliable transcript fetching.
- Added support for signed caption URLs and proper bot/rate-limit error handling.
- Improved language selection: prefers manual captions over auto-generated, supports language prefix matching.

### Changed

- `yt_transcript.transcript` now uses `InnertubeClient` internally.
- Updated documentation to reflect the Data API + Innertube architecture.

## [0.1.0] - 2025-01-01

### Added

- Initial release of `yt-transcript`.
- `setup` command to persistently store the YouTube Data API key.
- `--ext-api` flag for one-off API key overrides.
- Support for fetching transcripts via YouTube's timedtext endpoint.
- Output formats: `text`, `json`, `srt`, `vtt`.
- `--lang`, `--translate`, `--list-languages`, `--output`, and `--timeout` flags.
- Full unit test suite (52 tests) using only the Python standard library.
- Zero external dependencies.
