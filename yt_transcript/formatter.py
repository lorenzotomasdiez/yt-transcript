"""Output formatting for transcript segments."""

import json


def _format_time_srt(seconds):
    """Convert seconds to SRT time format HH:MM:SS,mmm."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def _format_time_vtt(seconds):
    """Convert seconds to VTT time format HH:MM:SS.mmm."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def _format_text(segments):
    return "\n".join(seg["text"] for seg in segments)


def _format_json(segments):
    return json.dumps(segments, indent=2, ensure_ascii=False)


def _format_srt(segments):
    lines = []
    for idx, seg in enumerate(segments, start=1):
        start = seg["start"]
        end = seg["start"] + seg["duration"]
        lines.append(str(idx))
        lines.append(f"{_format_time_srt(start)} --> {_format_time_srt(end)}")
        lines.append(seg["text"])
        lines.append("")
    return "\n".join(lines).rstrip()


def _format_vtt(segments):
    lines = ["WEBVTT", ""]
    for seg in segments:
        start = seg["start"]
        end = seg["start"] + seg["duration"]
        lines.append(f"{_format_time_vtt(start)} --> {_format_time_vtt(end)}")
        lines.append(seg["text"])
        lines.append("")
    return "\n".join(lines).rstrip()


_FORMATTERS = {
    "text": _format_text,
    "json": _format_json,
    "srt": _format_srt,
    "vtt": _format_vtt,
}


def format_transcript(segments, fmt):
    """Format a list of transcript segments into the requested output format.

    Supported formats: text, json, srt, vtt.
    """
    if fmt not in _FORMATTERS:
        raise ValueError(f"Unsupported format '{fmt}'. Choose from: text, json, srt, vtt.")
    return _FORMATTERS[fmt](segments)
