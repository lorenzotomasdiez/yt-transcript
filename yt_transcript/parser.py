"""YouTube URL parsing utilities."""

import re
from urllib.parse import parse_qs, urlparse

from yt_transcript.exceptions import InvalidVideoError

VIDEO_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{11}$")


def is_valid_video_id(video_id):
    """Return True if the string is a valid 11-character YouTube video id."""
    return bool(video_id) and bool(VIDEO_ID_PATTERN.match(video_id))


def extract_video_id(value):
    """Extract an 11-character video id from a URL or raw id string.

    Raises InvalidVideoError if the input cannot be parsed.
    """
    value = value.strip()

    if is_valid_video_id(value):
        return value

    parsed = urlparse(value)
    netloc = parsed.netloc.lower().lstrip("www.")

    if netloc in ("youtube.com", "m.youtube.com", "www.youtube.com"):
        if parsed.path.startswith("/watch"):
            query = parse_qs(parsed.query)
            video_id = query.get("v", [""])[0]
            if is_valid_video_id(video_id):
                return video_id
        elif parsed.path.startswith("/embed/"):
            video_id = parsed.path.split("/")[2]
            if is_valid_video_id(video_id):
                return video_id
        elif parsed.path.startswith("/shorts/"):
            video_id = parsed.path.split("/")[2]
            if is_valid_video_id(video_id):
                return video_id

    if netloc == "youtu.be":
        video_id = parsed.path.strip("/").split("/")[0]
        if is_valid_video_id(video_id):
            return video_id

    raise InvalidVideoError(f"Invalid video: could not extract a valid video id from '{value}'.")
