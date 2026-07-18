"""YouTube Data API v3 client."""

import json
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from yt_transcript.exceptions import APIError, VideoUnavailable

API_BASE = "https://www.googleapis.com/youtube/v3"


class YouTubeDataAPI:
    """Minimal client for the YouTube Data API captions endpoint."""

    def __init__(self, api_key, timeout=30):
        self.api_key = api_key
        self.timeout = timeout

    def _request(self, path, params):
        """Build and execute a GET request, returning parsed JSON."""
        params["key"] = self.api_key
        url = f"{API_BASE}{path}?{urlencode(params)}"
        req = Request(url, headers={"Accept": "application/json"})
        try:
            with urlopen(req, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            body = exc.read().decode("utf-8", errors="ignore")
            try:
                detail = json.loads(body)
                message = detail.get("error", {}).get("message", body or exc.reason)
            except json.JSONDecodeError:
                message = body or exc.reason

            if exc.code == 404:
                raise VideoUnavailable(params.get("videoId")) from exc
            raise APIError(message, status_code=exc.code) from exc

    def list_captions(self, video_id):
        """Return a list of caption tracks for the given video id."""
        data = self._request("/captions", {"part": "snippet", "videoId": video_id})
        tracks = []
        for item in data.get("items", []):
            snippet = item.get("snippet", {})
            tracks.append(
                {
                    "id": item.get("id"),
                    "language": snippet.get("language"),
                    "name": snippet.get("name"),
                    "is_auto": bool(snippet.get("isAutoSynced")),
                    "video_id": snippet.get("videoId"),
                }
            )
        return tracks
