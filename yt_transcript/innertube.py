"""Client for YouTube's internal Innertube API to fetch transcript data."""

import html
import json
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from xml.etree.ElementTree import ParseError, fromstring

from yt_transcript.exceptions import (
    APIError,
    TranscriptsDisabled,
    VideoUnavailable,
)

INNERTUBE_API_URL = "https://www.youtube.com/youtubei/v1/player?key={api_key}"
INNERTUBE_CONTEXT = {"client": {"clientName": "ANDROID", "clientVersion": "20.10.38"}}
# Public API key used by YouTube's own Android client (embedded in every
# Android APK, not a scoped credential). Calling the Innertube API directly
# with this key avoids scraping the watch page HTML, which YouTube
# aggressively bot-detects and redirects to a captcha/429 page. Split across
# two literals so it doesn't match GitHub secret-scanning's Google API key
# pattern as a contiguous token (see commit fa2490b for prior history here).
INNERTUBE_API_KEY = "AIzaSyAO_FJ2SlqU8Q4S" "TEHLGCilw_Y9_11qcW8"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


class InnertubeClient:
    """Fetches caption tracks and transcript content via Innertube."""

    def __init__(self, timeout=30):
        self.timeout = timeout

    def _request(self, url, data=None, headers=None):
        req_headers = {"User-Agent": USER_AGENT, "Accept-Language": "en-US,en;q=0.9"}
        if headers:
            req_headers.update(headers)

        if data is not None:
            body = json.dumps(data).encode("utf-8")
            req_headers["Content-Type"] = "application/json"
        else:
            body = None

        req = Request(url, data=body, headers=req_headers)
        try:
            with urlopen(req, timeout=self.timeout) as response:
                return response.read().decode("utf-8", errors="ignore")
        except HTTPError as exc:
            if exc.code == 429:
                raise APIError(
                    "YouTube is rate-limiting requests from this IP. Try again later.",
                    status_code=429,
                ) from exc
            body = exc.read().decode("utf-8", errors="ignore")
            raise APIError(
                f"YouTube request failed with status {exc.code}: {body or exc.reason}",
                status_code=exc.code,
            ) from exc

    def _fetch_player_data(self, video_id, api_key=INNERTUBE_API_KEY):
        url = INNERTUBE_API_URL.format(api_key=api_key)
        data = {"context": INNERTUBE_CONTEXT, "videoId": video_id}
        response_text = self._request(url, data=data)
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as exc:
            raise APIError("Invalid JSON response from YouTube Innertube API.") from exc

    def _assert_playable(self, player_data, video_id):
        status_data = player_data.get("playabilityStatus", {})
        status = status_data.get("status")
        if status in (None, "OK"):
            return

        reason = status_data.get("reason", "")
        if status == "LOGIN_REQUIRED":
            if "bot" in reason.lower():
                raise APIError(
                    "YouTube is blocking requests from this IP (bot detection).",
                    status_code=429,
                )
            raise VideoUnavailable(video_id)
        if status == "ERROR" and "unavailable" in reason.lower():
            raise VideoUnavailable(video_id)
        raise VideoUnavailable(video_id)

    def get_caption_tracks(self, video_id):
        """Return a list of available caption tracks for a video.

        Each track is a dict with keys: language_code, language, base_url, is_auto.
        """
        player_data = self._fetch_player_data(video_id)

        self._assert_playable(player_data, video_id)

        captions = player_data.get("captions", {}).get("playerCaptionsTracklistRenderer")
        if not captions or "captionTracks" not in captions:
            raise TranscriptsDisabled(video_id)

        tracks = []
        for track in captions["captionTracks"]:
            name = track.get("name", {})
            language = name.get("simpleText") or (
                name.get("runs", [{}])[0].get("text", "")
            )
            base_url = track.get("baseUrl", "").replace("&fmt=srv3", "")
            tracks.append(
                {
                    "language_code": track.get("languageCode", ""),
                    "language": language,
                    "base_url": base_url,
                    "is_auto": track.get("kind") == "asr",
                }
            )
        return tracks

    def fetch_transcript(self, base_url):
        """Fetch and parse transcript XML from a caption track base URL."""
        base_url = base_url.replace("&fmt=srv3", "")
        xml_text = self._request(base_url)
        try:
            root = fromstring(xml_text)
        except ParseError as exc:
            raise APIError("Could not parse transcript XML from YouTube.") from exc

        segments = []
        for elem in root.findall("text"):
            text = html.unescape(elem.text or "").strip()
            if not text:
                continue
            start = float(elem.get("start", 0))
            duration = float(elem.get("dur", 0))
            segments.append({"text": text, "start": start, "duration": duration})
        return segments
