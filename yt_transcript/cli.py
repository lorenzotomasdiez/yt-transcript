"""Command-line interface for yt-transcript."""

import argparse
import sys

from yt_transcript.api import YouTubeDataAPI
from yt_transcript.config import Config
from yt_transcript.exceptions import YTTranscriptError
from yt_transcript.formatter import format_transcript
from yt_transcript.parser import extract_video_id
from yt_transcript.transcript import fetch_transcript


def _build_setup_parser():
    parser = argparse.ArgumentParser(prog="yt-transcript setup")
    parser.add_argument(
        "--api-key",
        help="YouTube Data API key (if omitted, you will be prompted securely)",
    )
    return parser


def _build_fetch_parser():
    parser = argparse.ArgumentParser(prog="yt-transcript")
    parser.add_argument("video", help="YouTube URL or video id")
    parser.add_argument(
        "--ext-api",
        help="Use a different API key for this call only",
    )
    parser.add_argument(
        "--lang",
        help="Caption language code (e.g. en, es). Defaults to the first available track",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json", "srt", "vtt"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--translate",
        help="Translate captions into this language code",
    )
    parser.add_argument(
        "--list-languages",
        action="store_true",
        help="List available caption languages and exit",
    )
    parser.add_argument(
        "--output",
        help="Write output to this file instead of stdout",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="HTTP timeout in seconds (default: 30)",
    )
    return parser


def parse_args(argv=None):
    """Parse command-line arguments.

    Supports 'yt-transcript setup ...' and 'yt-transcript <video> ...'.
    """
    argv = list(sys.argv[1:] if argv is None else argv)

    if argv and argv[0] == "setup":
        parser = _build_setup_parser()
        args = parser.parse_args(argv[1:])
        args.command = "setup"
        return args

    parser = _build_fetch_parser()
    args = parser.parse_args(argv)
    args.command = "fetch"
    return args


def _resolve_api_key(args):
    """Return the API key to use for a transcript operation."""
    if args.ext_api:
        return args.ext_api
    config = Config()
    key = config.get_api_key()
    if not key:
        print(
            "Error: API key not configured. Run 'yt-transcript setup' first or use '--ext-api'.",
            file=sys.stderr,
        )
        return None
    return key


def _list_languages(api, video_id):
    """Print available caption languages."""
    tracks = api.list_captions(video_id)
    if not tracks:
        print("No caption tracks found.")
        return 0

    print("Available caption tracks:")
    for track in tracks:
        auto = " (auto)" if track["is_auto"] else ""
        print(f"  {track['language']}{auto} - {track['name']}")
    return 0


def _fetch_transcript(args, api, video_id):
    """Fetch and output a transcript."""
    language = args.lang
    if not language:
        tracks = api.list_captions(video_id)
        if not tracks:
            print("Error: No caption tracks found for this video.", file=sys.stderr)
            return 1
        language = tracks[0]["language"]

    segments = fetch_transcript(
        video_id,
        language=language,
        translate=args.translate,
        timeout=args.timeout,
    )
    output = format_transcript(segments, args.format)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(output)
            fh.write("\n")
    else:
        print(output)

    return 0


def run(args):
    """Execute the requested command."""
    if args.command == "setup":
        Config().setup(api_key=args.api_key)
        print("API key configured successfully.")
        return 0

    if args.command == "fetch":
        api_key = _resolve_api_key(args)
        if not api_key:
            return 1

        try:
            video_id = extract_video_id(args.video)
        except YTTranscriptError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1

        api = YouTubeDataAPI(api_key=api_key, timeout=args.timeout)

        if args.list_languages:
            return _list_languages(api, video_id)

        return _fetch_transcript(args, api, video_id)

    print(
        "Error: No command provided. Use 'yt-transcript setup' or 'yt-transcript <video>'.",
        file=sys.stderr,
    )
    return 1


def main(argv=None):
    """Entry point for the CLI."""
    args = parse_args(argv)
    try:
        return run(args)
    except YTTranscriptError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
