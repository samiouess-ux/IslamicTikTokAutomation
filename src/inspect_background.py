"""Inspect a single Mixkit stock-video URL before it is considered for rendering.

This tool checks file integrity and technical properties only. It does NOT
verify copyright/license status or approve a clip for production.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import urllib.parse
import urllib.request
from pathlib import Path

ALLOWED_HOSTS = {"assets.mixkit.co"}
MAX_BYTES = 100 * 1024 * 1024


def download(url: str, destination: Path) -> int:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
        raise SystemExit("Only HTTPS direct video URLs hosted on assets.mixkit.co are accepted.")
    request = urllib.request.Request(url, headers={"User-Agent": "IslamicTikTokAutomation/1.0"})
    total = 0
    with urllib.request.urlopen(request, timeout=60) as response, destination.open("wb") as out:
        content_type = response.headers.get("Content-Type", "")
        if "video" not in content_type and "octet-stream" not in content_type:
            raise SystemExit(f"Unexpected content type: {content_type or 'missing'}")
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_BYTES:
                raise SystemExit("Video exceeds the 100 MB inspection limit.")
            out.write(chunk)
    if total == 0:
        raise SystemExit("Downloaded file is empty.")
    return total


def probe(path: Path) -> dict:
    raw = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)
    ], text=True)
    data = json.loads(raw)
    video = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), None)
    if not video:
        raise SystemExit("No video stream found.")
    width, height = int(video["width"]), int(video["height"])
    fps_text = video.get("avg_frame_rate", "0/1")
    numerator, denominator = fps_text.split("/")
    fps = float(numerator) / float(denominator) if float(denominator) else 0
    duration = float(data.get("format", {}).get("duration", 0))
    has_audio = any(s.get("codec_type") == "audio" for s in data.get("streams", []))
    return {
        "container": data.get("format", {}).get("format_name"),
        "video_codec": video.get("codec_name"),
        "width": width,
        "height": height,
        "fps": round(fps, 3),
        "duration_seconds": round(duration, 3),
        "has_audio_stream": has_audio,
        "portrait": height > width,
        "recommended_for_9_16": height > width and (height / width) >= 1.65,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="Direct Mixkit MP4 URL")
    parser.add_argument("--source-page", required=True, help="Mixkit item page URL")
    parser.add_argument("--title", required=True, help="Short candidate label")
    parser.add_argument("--output-dir", default="background_inspection")
    args = parser.parse_args()

    page = urllib.parse.urlparse(args.source_page)
    if page.scheme != "https" or page.hostname != "mixkit.co":
        raise SystemExit("Source page must be an HTTPS Mixkit item page.")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    video_path = output_dir / "candidate.mp4"
    size_bytes = download(args.url, video_path)
    technical = probe(video_path)
    report = {
        "title": args.title,
        "source_page": args.source_page,
        "direct_video_url": args.url,
        "downloaded_bytes": size_bytes,
        "technical_inspection": technical,
        "license": {
            "status": "not_automatically_verified",
            "required_manual_check": "Confirm this exact item page labels the clip Mixkit Stock Video Free License, not Restricted License."
        },
        "production": {
            "approved": False,
            "user_approved": False,
            "status": "inspection_only"
        }
    }
    report_path = output_dir / "inspection.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not technical["recommended_for_9_16"]:
        raise SystemExit("Inspection completed, but the clip is not a recommended portrait 9:16 source.")


if __name__ == "__main__":
    main()
