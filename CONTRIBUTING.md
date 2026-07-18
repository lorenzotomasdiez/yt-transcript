# Contributing to yt-transcript

Thanks for your interest in contributing! This document explains how to set up
your development environment and the workflow we follow.

## Getting started

1. Fork the repository on GitHub.
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/yt-transcript.git
   cd yt-transcript
   ```
3. Create a virtual environment and install the package in editable mode:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```

## Development workflow

- We use **TDD** (test-driven development). Write failing tests before adding
  or changing functionality.
- Keep the code **dependency-free**; only the Python standard library is
  allowed.
- Run the full test suite before opening a pull request:
  ```bash
  python3 -m unittest discover -s tests -v
  ```
- Keep changes small and focused. One feature or fix per PR.

## Coding style

- Follow PEP 8 and use `snake_case` for functions/variables and
  `PascalCase` for classes.
- Add docstrings for public modules, classes, and functions.
- Prefer explicit error messages and domain exceptions from
  `yt_transcript.exceptions`.

## Pull requests

- Update `README.md` and `CHANGELOG.md` if your change is user-facing.
- Make sure CI passes (GitHub Actions runs the test suite on multiple Python
  versions).
- Fill out the pull request template completely.

## Reporting bugs / requesting features

Use the GitHub issue templates:
- **Bug report** — for crashes, incorrect behavior, or unexpected errors.
- **Feature request** — for new capabilities or improvements.

## License

By contributing, you agree that your contributions will be licensed under the
MIT License.
