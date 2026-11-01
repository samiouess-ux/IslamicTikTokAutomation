"""Download staged background clips into a temporary review-only preview package."""
from __future__ import annotations

import argparse
import json
import subprocess
import urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


MAX_DOWNLOAD_BYTES = 100 * 1024 * 1024
USER_AGENT = "IslamicTikTokAutomation/1.0 (background-review-only)"


def download_candidate(url: str, destination: Path) -> int:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    total = 0
    with urllib.request.urlopen(request, timeout=90) as response, destination.open("wb") as target:
        content_type = response.headers.get("Content-Type", "").lower()
        if "video" not in content_type and "octet-stream" not in content_type:
            raise RuntimeError(f"Unexpected content type for video download: {content_type}")
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_DOWNLOAD_BYTES:
                raise RuntimeError("Background candidate exceeds the 100 MiB review-download limit.")
            target.write(chunk)
    if total == 0:
        raise RuntimeError("Downloaded background candidate is empty.")
    return total


def probe_video(path: Path) -> dict:
    raw = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration,size:stream=codec_type,codec_name,width,height",
        "-of", "json", str(path)
    ], text=True)
    data = json.loads(raw)
    video = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), None)
    if not video or not video.get("width") or not video.get("height"):
        raise RuntimeError(f"No valid video stream found in {path.name}")
    duration = float(data.get("format", {}).get("duration", 0))
    if duration <= 0:
        raise RuntimeError(f"Invalid duration in {path.name}")
    return {
        "width": int(video["width"]),
        "height": int(video["height"]),
        "duration_seconds": round(duration, 3),
        "video_codec": video.get("codec_name"),
    }


def extract_vertical_crop(source: Path, destination: Path, duration: float) -> None:
    timestamp = max(0.1, duration / 2)
    subprocess.run([
        "ffmpeg", "-y", "-ss", str(timestamp), "-i", str(source),
        "-frames:v", "1", "-vf",
        "scale=540:960:force_original_aspect_ratio=increase,crop=540:960",
        "-q:v", "2", str(destination)
    ], check=True, capture_output=True, text=True)
    with Image.open(destination) as image:
        if image.size != (540, 960):
            raise RuntimeError(f"Vertical crop has unexpected dimensions: {image.size}")


def build_contact_sheet(items: list[dict], output: Path) -> None:
    sheet = Image.new("RGB", (1080, 1920), (10, 16, 22))
    draw = ImageDraw.Draw(sheet)
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    title_font = ImageFont.truetype(font_path, 22)
    note_font = ImageFont.truetype(font_path, 16)
    for index, item in enumerate(items):
        x = (index % 2) * 540
        y = (index // 2) * 960
        with Image.open(item["preview_path"]) as image:
            sheet.paste(image.convert("RGB"), (x, y))
        draw.rectangle((x, y, x + 540, y + 86), fill=(0, 0, 0))
        draw.text((x + 16, y + 12), item["description"][:42], font=title_font, fill=(255, 255, 255))
        dims = f'{item["width"]}x{item["height"]}  |  {item["duration_seconds"]}s  |  center crop 9:16'
        draw.text((x + 16, y + 48), dims, font=note_font, fill=(238, 211, 153))
    sheet.save(output, quality=90)


def prepare(catalog_path: Path, output_dir: Path) -> dict:
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    candidates = catalog.get("candidates", [])
    if len(candidates) != 4:
        raise RuntimeError("Expected exactly four staged background candidates.")
    output_dir.mkdir(parents=True, exist_ok=True)
    items = []
    for candidate in candidates:
        if candidate.get("approved") or candidate.get("user_approved") or candidate.get("download_verified"):
            raise RuntimeError("This review workflow accepts only disabled, unverified candidates.")
        url = candidate.get("direct_video_url", "")
        if not url.startswith("https://videos.pexels.com/video-files/"):
            raise RuntimeError(f"Untrusted or missing candidate URL: {candidate.get('id')}")
        video_path = output_dir / f'{candidate["id"]}.mp4'
        preview_path = output_dir / f'{candidate["id"]}_vertical_crop.jpg'
        byte_count = download_candidate(url, video_path)
        metadata = probe_video(video_path)
        extract_vertical_crop(video_path, preview_path, metadata["duration_seconds"])
        items.append({
            "id": candidate["id"],
            "description": candidate["description"],
            "creator": candidate["creator"],
            "source_page_url": candidate["source_page_url"],
            "license_note": candidate["license"],
            "download_bytes": byte_count,
            "preview_path": str(preview_path),
            **metadata,
            "download_probe_verified": True,
            "visual_approval": False,
            "production_enabled": False,
            "user_approved": False,
        })
    contact_sheet = output_dir / "background_candidates_contact_sheet.jpg"
    build_contact_sheet(items, contact_sheet)
    report = {
        "status": "downloaded_and_probe_verified_requires_user_visual_review",
        "candidate_count": len(items),
        "contact_sheet": str(contact_sheet),
        "production_enabled": False,
        "user_approval_required": True,
        "items": [{k: v for k, v in item.items() if k != "preview_path"} for item in items],
    }
    (output_dir / "background_review_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", default="data/background_candidates.json")
    parser.add_argument("--output-dir", default="output/background_review")
    args = parser.parse_args()
    report = prepare(Path(args.catalog), Path(args.output_dir))
    print(f"Prepared {report['candidate_count']} review-only background crops.")
    print("No background was activated; explicit user approval is still required.")


if __name__ == "__main__":
    main()
