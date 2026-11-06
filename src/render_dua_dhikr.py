"""Dedicated review-only renderer for sourced dua and adhkar items.

This module deliberately does not import or call the Quran renderer.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, features
from validate_content_manifest import validate_content_manifest

MAX_VIDEO_SECONDS = 40.0
WIDTH, HEIGHT = 1080, 1920


def download(url: str, destination: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": "IslamicTikTokAutomation-Pro/1.0"})
    with urllib.request.urlopen(request, timeout=90) as response, destination.open("wb") as out:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def _font_path() -> str:
    try:
        path = subprocess.check_output(
            ["fc-match", "-f", "%{file}", "Amiri:style=Bold"], text=True
        ).strip()
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        raise SystemExit("Amiri Bold is required for safe Arabic rendering.") from exc
    if not path or not Path(path).is_file():
        raise SystemExit(f"Amiri Bold font is missing: {path!r}")
    return path


def _wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont,
          max_width: int, direction: str | None = None) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = (current + " " + word).strip()
        kwargs = {"direction": direction, "language": "ar"} if direction else {}
        if draw.textbbox((0, 0), candidate, font=font, **kwargs)[2] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def create_item_overlay(item: dict, destination: Path, template: str = "ornate_gold_classic") -> None:
    """Create a transparent 9:16 card; Arabic source wording is never rewritten."""
    if template not in {"ornate_gold_classic", "nature_clean", "minimal_mushaf", "cinematic_landscape"}:
        raise SystemExit(f"Unsupported dua/dhikr template: {template}")
    if not features.check("raqm"):
        raise SystemExit("Arabic rendering blocked: Pillow libraqm/RAQM is unavailable.")
    arabic = item.get("arabic")
    if not isinstance(arabic, str) or not arabic.strip():
        raise SystemExit("Item has no exact Arabic wording.")
    font_path = _font_path()
    image = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    gold = (231, 190, 103, 255)
    ivory = (255, 250, 235, 255)
    panel = (7, 12, 18, 205)
    draw.rounded_rectangle((72, 360, 1008, 1515), radius=58, fill=panel,
                           outline=gold, width=4)
    draw.rounded_rectangle((94, 382, 986, 1493), radius=42,
                           outline=(gold[0], gold[1], gold[2], 115), width=2)
    title = item.get("display_title") or ("ذِكْر" if item.get("kind") == "dhikr" else "دُعَاء")
    title_font = ImageFont.truetype(font_path, 68)
    draw.text((540, 535), title, font=title_font, fill=gold, anchor="mm",
              direction="rtl", language="ar")
    draw.line((290, 625, 790, 625), fill=gold, width=3)

    chosen = None
    for size in (76, 70, 64, 58, 52, 48, 44):
        font = ImageFont.truetype(font_path, size)
        lines = _wrap(draw, arabic, font, 820, "rtl")
        if len(lines) <= 7:
            chosen = (font, lines)
            break
    if chosen is None:
        raise SystemExit("Arabic wording is too long for the safe layout; split it into reviewed items.")
    font, lines = chosen
    line_height = font.size * 1.75
    block_height = len(lines) * line_height
    start_y = 930 - block_height / 2
    for index, line in enumerate(lines):
        draw.text((540, start_y + index * line_height), line, font=font, fill=ivory,
                  anchor="mm", direction="rtl", language="ar")

    meaning = item.get("meaning_en")
    if meaning:
        meaning_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
        meaning_lines = _wrap(draw, str(meaning), meaning_font, 800)
        if len(meaning_lines) > 4:
            raise SystemExit("English meaning exceeds the safe layout.")
        y = 1240 - (len(meaning_lines) - 1) * 43 / 2
        for line in meaning_lines:
            draw.text((540, y), line, font=meaning_font, fill=(255, 255, 255, 255), anchor="mm")
            y += 43

    repeat_count = item.get("repeat_count")
    if repeat_count is not None:
        small = ImageFont.truetype(font_path, 34)
        repeat_text = f"التكرار: {repeat_count}".translate(
            str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
        )
        draw.text((540, 1395), repeat_text, font=small, fill=gold, anchor="mm",
                  direction="rtl", language="ar")
    image.save(destination)


def _duration(audio: dict) -> float:
    if audio.get("kind") == "silent":
        value = audio.get("duration_seconds")
        if not isinstance(value, (int, float)) or value <= 0:
            raise SystemExit("Silent audio requires a positive duration_seconds.")
        return float(value)
    audio_file = Path(str(audio.get("file", "")))
    if not audio_file.is_file():
        raise SystemExit(f"Approved audio file is missing: {audio_file}")
    raw = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=nw=1:nk=1", str(audio_file)
    ], text=True).strip()
    return float(raw)


def render_manifest(manifest_path: Path, output_path: Path) -> dict:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    validate_content_manifest(data)
    if data.get("content_type") not in {"dua", "dhikr"}:
        raise SystemExit("Dedicated Pro renderer accepts dua or dhikr manifests only.")
    if len(data["items"]) != 1:
        raise SystemExit("One reviewed dua/dhikr item is required per video.")
    if data.get("publishing", {}).get("auto_publish", False):
        raise SystemExit("Automatic publishing is prohibited.")
    item = data["items"][0]
    audio = data["audio"]
    duration = _duration(audio)
    if duration > MAX_VIDEO_SECONDS:
        raise SystemExit(f"Video duration {duration:.2f}s exceeds {MAX_VIDEO_SECONDS:.0f}s.")
    work = Path("build/dua_dhikr")
    work.mkdir(parents=True, exist_ok=True)
    background_file = work / "background.mp4"
    overlay_file = work / "item_overlay.png"
    background_url = data["visual"]["background_candidate"]["direct_video_url"]
    download(background_url, background_file)
    create_item_overlay(item, overlay_file, data["visual"].get("template", "ornate_gold_classic"))
    output_path.parent.mkdir(parents=True, exist_ok=True)

    command = ["ffmpeg", "-y", "-stream_loop", "-1", "-i", str(background_file)]
    if audio.get("kind") == "silent":
        command += ["-f", "lavfi", "-t", str(duration), "-i", "anullsrc=r=48000:cl=stereo"]
    else:
        command += ["-i", str(audio["file"])]
    command += ["-loop", "1", "-framerate", "30", "-t", str(duration), "-i", str(overlay_file)]
    command += [
        "-filter_complex",
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        "setsar=1,fps=30,drawbox=x=45:y=330:w=990:h=1220:color=black@0.22:t=fill[bg];"
        "[bg][2:v]overlay=0:0:format=auto[v]",
        "-map", "[v]", "-map", "1:a", "-t", str(duration),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(output_path)
    ]
    run(command)
    if not output_path.is_file() or output_path.stat().st_size == 0:
        raise SystemExit("FFmpeg did not produce a non-empty review MP4.")
    return {
        "status": "rendered_for_manual_review",
        "content_type": data["content_type"],
        "content_id": item["id"],
        "output": str(output_path),
        "duration_seconds": duration,
        "telegram_sent": False,
        "tiktok_published": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Render one sourced dua/dhikr item for manual review.")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output", default="output/dua_dhikr_review.mp4")
    args = parser.parse_args()
    print(json.dumps(render_manifest(Path(args.manifest), Path(args.output)),
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
