"""Allow running the package as a module: python -m yt_transcript."""

import sys

from yt_transcript.cli import main

if __name__ == "__main__":
    sys.exit(main())
