"""Manifest-driven Quran video renderer with strict Arabic text preservation."""
from __future__ import annotations

import argparse
import json
import subprocess
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, features


def download(url: str, destination: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": "IslamicTikTokAutomation/1.0"})
    with urllib.request.urlopen(request, timeout=90) as response, destination.open("wb") as out:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)


def ffmpeg_text(value: str) -> str:
    return (value.replace("\\", "\\\\").replace(":", "\\:")
            .replace("'", "\\'").replace("%", "\\%")
            .replace(",", "\\,").replace("[", "\\[").replace("]", "\\]"))


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def create_arabic_overlay(title: str, verses: list[dict], destination: Path) -> None:
    """Shape Arabic with libraqm; never normalize, strip, or rewrite Quran text."""
    if not features.check("raqm"):
        raise SystemExit("Arabic rendering blocked: Pillow libraqm/RAQM is unavailable.")
    font_path = "/usr/share/fonts/truetype/noto/NotoNaskhArabic-Regular.ttf"
    if not Path(font_path).exists():
        raise SystemExit("Arabic font not found; refusing to render Quran text.")
    image = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    title_font = ImageFont.truetype(font_path, 48)
    verse_font = ImageFont.truetype(font_path, 76)

    # Ornate classical Islamic cartouche: pointed ends, layered borders,
    # rosette details and corner arabesques. All decoration stays outside text.
    gold = (231, 190, 103, 255)
    soft_gold = (231, 190, 103, 190)
    faint_gold = (231, 190, 103, 105)

    # Main title cartouche with pointed ends and gently scalloped shoulders.
    outer = [(540, 392), (575, 410), (785, 410), (815, 430),
             (845, 475), (815, 520), (785, 540), (575, 540),
             (540, 558), (505, 540), (295, 540), (265, 520),
             (235, 475), (265, 430), (295, 410), (505, 410)]
    inner = [(540, 405), (568, 420), (780, 420), (802, 437),
             (829, 475), (802, 513), (780, 530), (568, 530),
             (540, 545), (512, 530), (300, 530), (278, 513),
             (251, 475), (278, 437), (300, 420), (512, 420)]
    draw.line(outer + [outer[0]], fill=gold, width=4, joint="curve")
    draw.line(inner + [inner[0]], fill=faint_gold, width=2, joint="curve")

    # Small eight-petal rosettes at both ends of the cartouche.
    def rosette(cx: int, cy: int, radius: int, color) -> None:
        for angle in range(0, 360, 45):
            import math
            rad = math.radians(angle)
            px, py = cx + math.cos(rad) * radius * 0.62, cy + math.sin(rad) * radius * 0.62
            draw.ellipse((px - radius * 0.38, py - radius * 0.38,
                          px + radius * 0.38, py + radius * 0.38),
                         outline=color, width=2)
        draw.ellipse((cx - 3, cy - 3, cx + 3, cy + 3), fill=color)

    rosette(282, 475, 17, gold)
    rosette(798, 475, 17, gold)
    for x in (335, 745):
        draw.polygon([(x, 414), (x + 7, 425), (x, 436), (x - 7, 425)],
                     outline=soft_gold)
        draw.polygon([(x, 514), (x + 7, 525), (x, 536), (x - 7, 525)],
                     outline=soft_gold)

    draw.text((540, 475), title, font=title_font, fill=gold,
              anchor="mm", direction="rtl", language="ar", stroke_width=0)
    line_gap = 145 if len(verses) <= 3 else 115
    first_y = 700 if len(verses) <= 3 else 620
    for index, verse in enumerate(verses):
        exact_text = verse["arabic"]
        if not isinstance(exact_text, str) or not exact_text.strip():
            raise SystemExit("Invalid/empty Arabic verse text.")

        y = first_y + index * line_gap
        # Draw the Quran text alone, unchanged. Do not append a marker to it.
        draw.text((540, y), exact_text, font=verse_font,
                  fill=(255, 255, 255, 255), anchor="mm",
                  direction="rtl", language="ar", stroke_width=0)

        # Place a separate, small verse-number medallion just after the
        # visual end of the RTL line, with a clear gap from the letters.
        bbox = draw.textbbox((540, y), exact_text, font=verse_font,
                             anchor="mm", direction="rtl", language="ar")
        medallion_radius = 27
        gap = 48
        cx = bbox[0] - gap - medallion_radius
        cy = y
        # Eight-lobed ornamental verse cartouche, separate from Quran text.
        import math
        points = []
        for angle in range(0, 360, 15):
            radius = medallion_radius if (angle // 15) % 2 == 0 else medallion_radius - 5
            rad = math.radians(angle)
            points.append((cx + math.cos(rad) * radius, cy + math.sin(rad) * radius))
        draw.line(points + [points[0]], fill=gold, width=3, joint="curve")
        draw.ellipse((cx - 19, cy - 19, cx + 19, cy + 19),
                     outline=soft_gold, width=2)
        number_font = ImageFont.truetype(font_path, 27)
        number = str(verse["number"]).translate(str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩"))
        draw.text((cx, cy), number, font=number_font,
                  fill=gold, anchor="mm", direction="rtl", language="ar")
    image.save(destination)


def create_english_overlay(verses: list[dict], destination: Path) -> None:
    """Render each translation separately, wrapped and centered."""
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    if not Path(font_path).exists():
        raise SystemExit("English font not found.")
    image = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_path, 36)
    blocks = []
    for verse in verses:
        lines, current = [], ""
        for word in verse["english"].split():
            candidate = (current + " " + word).strip()
            if draw.textbbox((0, 0), candidate, font=font)[2] <= 900:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        blocks.append(lines)
    total = sum(len(block) for block in blocks) * 56 + max(0, len(blocks) - 1) * 18
    y = 1370 + max(0, (360 - total) // 2)
    for block in blocks:
        for line in block:
            draw.text((540, y), line, font=font, fill=(255, 255, 255, 255), anchor="mm")
            y += 56
        y += 18
    image.save(destination)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output", default="output/review.mp4")
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    source, audio, visual = data["source"], data["audio"], data["visual"]
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
    verse_numbers = [int(v["number"]) for v in verses]
    if len(set(verse_numbers)) != len(verse_numbers) or verse_numbers != sorted(verse_numbers):
        raise SystemExit("Verse numbers must be unique and in ascending Quran order.")
    # Do not normalize Unicode, remove harakat, or rewrite Arabic characters.
    for verse in verses:
        if not isinstance(verse.get("arabic"), str) or not verse["arabic"]:
            raise SystemExit("Every verse must contain exact Arabic source text.")
        if not verse.get("english"):
            raise SystemExit("Every verse must contain its paired English translation.")

    # Keep the on-screen title to Arabic letters only; verse range is in caption metadata.
    title = f"سورة {source['surah_name_ar']}"

    work = Path("build")
    work.mkdir(exist_ok=True)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    audio_file, bg_file = work / "recitation.mp3", work / "background.mp4"
    arabic_overlay = work / "arabic_text.png"
    english_overlay = work / "english_text.png"

    create_arabic_overlay(title, verses, arabic_overlay)
    create_english_overlay(verses, english_overlay)

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
    concat_list.write_text("".join("file '" + str(p.resolve()) + "'\n" for p in extracted), encoding="utf-8")
    run(["ffmpeg", "-hide_banner", "-y", "-f", "concat", "-safe", "0",
         "-i", str(concat_list), "-c", "copy", str(audio_file)])
    download(background_url, bg_file)

    duration_result = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=nw=1:nk=1", str(audio_file)
    ], text=True).strip()
    duration = float(duration_result)

    draw = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,setsar=1,fps=30,"
        "drawbox=x=55:y=380:w=970:h=1120:color=black@0.30:t=fill[v0];"
        "[v0][2:v]overlay=0:0[v1];"
        "[v1][3:v]overlay=0:0[v]"
    )
    run([
        "ffmpeg", "-hide_banner", "-y", "-stream_loop", "-1", "-i", str(bg_file),
        "-i", str(audio_file), "-i", str(arabic_overlay),
        "-i", str(english_overlay), "-filter_complex", draw,
        "-map", "[v]", "-map", "1:a", "-t", str(duration),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart", str(output)
    ])

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
