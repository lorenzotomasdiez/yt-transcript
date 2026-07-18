"""Fetch and parse YouTube transcript data using Innertube."""

from urllib.parse import urlencode

from yt_transcript.exceptions import LanguageUnavailable, TranscriptsDisabled
from yt_transcript.innertube import InnertubeClient


def _select_track(tracks, video_id, language):
    """Select the best caption track for the requested language.

    Prefers manually created captions over auto-generated ones.
    If language is None, returns the first available track.
    """
    if language is None:
        return tracks[0]

    # Exact language match, prefer manual over auto
    manual = [t for t in tracks if t["language_code"] == language and not t["is_auto"]]
    if manual:
        return manual[0]

    auto = [t for t in tracks if t["language_code"] == language and t["is_auto"]]
    if auto:
        return auto[0]

    # Prefix match (e.g., "en" matches "en-US")
    manual_prefix = [
        t for t in tracks if t["language_code"].startswith(language) and not t["is_auto"]
    ]
    if manual_prefix:
        return manual_prefix[0]

    auto_prefix = [
        t for t in tracks if t["language_code"].startswith(language) and t["is_auto"]
    ]
    if auto_prefix:
        return auto_prefix[0]

    raise LanguageUnavailable(video_id, language)


def fetch_transcript(video_id, language=None, translate=None, timeout=30):
    """Fetch transcript segments for a video.

    Args:
        video_id: 11-character YouTube video id.
        language: Optional BCP-47 language code. Defaults to first available track.
        translate: Optional language code to translate captions into.
        timeout: HTTP timeout in seconds.

    Returns:
        List of dicts with keys 'text', 'start', and 'duration'.
    """
    client = InnertubeClient(timeout=timeout)
    tracks = client.get_caption_tracks(video_id)

    if not tracks:
        raise TranscriptsDisabled(video_id)

    track = _select_track(tracks, video_id, language)

    base_url = track["base_url"]
    if translate:
        separator = "&" if "?" in base_url else "?"
        base_url = f"{base_url}{separator}{urlencode({'tlang': translate})}"

    segments = client.fetch_transcript(base_url)
    if not segments:
        raise TranscriptsDisabled(video_id)
    return segments
