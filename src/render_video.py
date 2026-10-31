"""Reusable manifest-driven renderer for reviewed Quran reminder videos.

The renderer deliberately requires explicit, pre-approved audio/background URLs.
It does not publish anything.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import urllib.request
from pathlib import Path


def download(url: str, destination: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": "IslamicTikTokAutomation/1.0"})
    with urllib.request.urlopen(request, timeout=90) as response, destination.open("wb") as out:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)


def ffmpeg_text(value: str) -> str:
    # Escape drawtext filter special characters.
    return (value.replace("\\", "\\\\").replace(":", "\\:")
            .replace("'", "\\'").replace("%", "\\%")
            .replace(",", "\\,").replace("[", "\\[").replace("]", "\\]"))


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output", default="output/review.mp4")
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    source = data["source"]
    audio = data["audio"]
    visual = data["visual"]
    caption = data.get("caption", {})

    background_url = visual.get("approved_background_url") or visual.get("background_candidate", {}).get("direct_video_url")
    if not background_url:
        raise SystemExit("Manifest must provide an approved background candidate URL.")
    if not audio.get("approved_for_first_test_video", audio.get("approved", False)):
        raise SystemExit("Audio is not marked approved. Refusing to render.")
    if not visual.get("background_candidate", {}).get("approved", False):
        raise SystemExit("Background is not marked approved. Refusing to render.")

    verses = data.get("verses", [])
    if not verses:
        raise SystemExit("Manifest has no verified verse text.")
    arabic = "   ".join(f"{v['arabic']} ۝{v['number']}" for v in verses)
    english = "\\n".join(v["english"] for v in verses)
    surah_ar = source["surah_name_ar"]
    verse_numbers = [int(v["number"]) for v in verses]
    range_label = (f"الآيات {verse_numbers[0]}–{verse_numbers[-1]}"
                   if len(verse_numbers) > 1 else f"الآية {verse_numbers[0]}")
    title = f"سورة {surah_ar} — {range_label}"

    work = Path("build")
    work.mkdir(exist_ok=True)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    audio_file, bg_file = work / "recitation.mp3", work / "background.mp4"
    from remotezip import RemoteZip
    archive_url = audio.get("official_verse_archive_url")
    if not archive_url:
        raise SystemExit("Manifest is missing the official verse archive URL.")
    archive_entries = audio.get("archive_entries", {})
    extracted = []
    with RemoteZip(archive_url) as archive:
        for number in verse_numbers:
            entry = archive_entries.get(str(number))
            if not entry:
                raise SystemExit(f"Missing approved archive entry for verse {number}.")
            target = work / f"verse_{number:03d}.mp3"
            with archive.open(entry) as src, target.open("wb") as dst:
                while True:
                    chunk = src.read(1024 * 1024)
                    if not chunk:
                        break
                    dst.write(chunk)
            extracted.append(target)
    concat_list = work / "audio_concat.txt"
    concat_list.write_text("".join("file '" + str(p.resolve()) + "'\\n" for p in extracted), encoding="utf-8")
    run(["ffmpeg", "-hide_banner", "-y", "-f", "concat", "-safe", "0",
         "-i", str(concat_list), "-c", "copy", str(audio_file)])
    download(background_url, bg_file)

    duration_result = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=nw=1:nk=1", str(audio_file)
    ], text=True).strip()
    duration = float(duration_result)

    font_ar = "/usr/share/fonts/truetype/noto/NotoNaskhArabic-Regular.ttf"
    font_en = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    if not Path(font_ar).exists():
        raise SystemExit("Arabic font not found on runner.")

    draw = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,setsar=1,fps=30,"
        "drawbox=x=55:y=380:w=970:h=1120:color=black@0.30:t=fill,"
        f"drawtext=fontfile={font_ar}:text='{ffmpeg_text(title)}':"
        "fontcolor=white:fontsize=42:x=(w-text_w)/2:y=450,"
        f"drawtext=fontfile={font_ar}:text='{ffmpeg_text(arabic)}':"
        "fontcolor=white:fontsize=68:line_spacing=24:text_shaping=1:"
        "x=(w-text_w)/2:y=650,"
        f"drawtext=fontfile={font_en}:text='{ffmpeg_text(english)}':"
        "fontcolor=white:fontsize=30:line_spacing=16:"
        "x=(w-text_w)/2:y=1120[v]"
    )
    run([
        "ffmpeg", "-hide_banner", "-y", "-stream_loop", "-1", "-i", str(bg_file),
        "-i", str(audio_file), "-filter_complex", draw,
        "-map", "[v]", "-map", "1:a", "-t", str(duration),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart", str(output)
    ])

    # Produce review caption separately; never publish.
    caption_path = output.with_suffix(".caption.json")
    caption_path.write_text(json.dumps({
        "status": "review_required",
        "surah": source["surah_name_ar"],
        "verses": verse_numbers,
        "arabic_caption": caption.get("arabic", ""),
        "english_caption": caption.get("english", ""),
        "hashtags_ar": caption.get("hashtags_ar", []),
        "hashtags_en": caption.get("hashtags_en", []),
        "reciter_public_attribution": False,
        "publishing": "disabled"
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Rendered review video: {output} ({duration:.2f}s)")
    print(f"Caption for review: {caption_path}")


if __name__ == "__main__":
    main()
