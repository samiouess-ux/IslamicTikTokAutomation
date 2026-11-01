"""Render strictly review-only Quran video previews from whole-ayah audio.

This renderer is separate from production rendering. It uses generated graphic
backgrounds (no third-party visual assets), exact catalog text, and the original
per-ayah MP3 streams. It never approves, sends, or publishes anything.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, features

SURAH_NAMES = [
    "الفاتحة",
    "البقرة",
    "آل عمران",
    "النساء",
    "المائدة",
    "الأنعام",
    "الأعراف",
    "الأنفال",
    "التوبة",
    "يونس",
    "هود",
    "يوسف",
    "الرعد",
    "إبراهيم",
    "الحجر",
    "النحل",
    "الإسراء",
    "الكهف",
    "مريم",
    "طه",
    "الأنبياء",
    "الحج",
    "المؤمنون",
    "النور",
    "الفرقان",
    "الشعراء",
    "النمل",
    "القصص",
    "العنكبوت",
    "الروم",
    "لقمان",
    "السجدة",
    "الأحزاب",
    "سبأ",
    "فاطر",
    "يس",
    "الصافات",
    "ص",
    "الزمر",
    "غافر",
    "فصلت",
    "الشورى",
    "الزخرف",
    "الدخان",
    "الجاثية",
    "الأحقاف",
    "محمد",
    "الفتح",
    "الحجرات",
    "ق",
    "الذاريات",
    "الطور",
    "النجم",
    "القمر",
    "الرحمن",
    "الواقعة",
    "الحديد",
    "المجادلة",
    "الحشر",
    "الممتحنة",
    "الصف",
    "الجمعة",
    "المنافقون",
    "التغابن",
    "الطلاق",
    "التحريم",
    "الملك",
    "القلم",
    "الحاقة",
    "المعارج",
    "نوح",
    "الجن",
    "المزمل",
    "المدثر",
    "القيامة",
    "الإنسان",
    "المرسلات",
    "النبأ",
    "النازعات",
    "عبس",
    "التكوير",
    "الانفطار",
    "المطففين",
    "الانشقاق",
    "البروج",
    "الطارق",
    "الأعلى",
    "الغاشية",
    "الفجر",
    "البلد",
    "الشمس",
    "الليل",
    "الضحى",
    "الشرح",
    "التين",
    "العلق",
    "القدر",
    "البينة",
    "الزلزلة",
    "العاديات",
    "القارعة",
    "التكاثر",
    "العصر",
    "الهمزة",
    "الفيل",
    "قريش",
    "الماعون",
    "الكوثر",
    "الكافرون",
    "النصر",
    "المسد",
    "الإخلاص",
    "الفلق",
    "الناس"
]

APPROVED_BACKGROUND_URL = "https://assets.mixkit.co/active_storage/video_items/100174/1721166924/100174-video-720.mp4"
BACKGROUND_SOURCE = "Mixkit — Waterfall Between Green Hills (previously user-approved)"

PALETTES = [
    ((12, 31, 46), (25, 68, 75), (220, 190, 125)),
    ((31, 24, 48), (67, 47, 82), (226, 203, 151)),
    ((18, 42, 34), (40, 79, 57), (213, 221, 175)),
    ((36, 31, 25), (83, 63, 43), (230, 205, 155)),
]


def download_background(url: str, destination: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": "IslamicTikTokAutomation/1.0"})
    with urllib.request.urlopen(request, timeout=90) as response, destination.open("wb") as target:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            target.write(chunk)


def font_file() -> str:
    result = subprocess.check_output(
        ["fc-match", "-f", "%{file}", "Noto Naskh Arabic"], text=True
    ).strip()
    if not result or not Path(result).is_file():
        raise RuntimeError("Noto Naskh Arabic font is required for Arabic preview rendering.")
    return result


def fit_translation_lines(draw: ImageDraw.ImageDraw, text: str, font_path: str,
                          max_width: int = 820, max_lines: int = 5):
    """Fit every translation word by reducing font size; never truncate text."""
    for size in (30, 28, 26, 24, 22):
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size
        )
        lines, current = [], ""
        for word in text.split():
            if draw.textbbox((0, 0), word, font=font)[2] > max_width:
                raise ValueError("A translation word is wider than the available text area.")
            candidate = (current + " " + word).strip()
            if draw.textbbox((0, 0), candidate, font=font)[2] <= max_width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        if len(lines) <= max_lines:
            return font, lines, max(42, size + 14)
    raise ValueError("Translation does not fit without clipping, even at the minimum font size.")


def fit_arabic_lines(draw: ImageDraw.ImageDraw, text: str, font_path: str,
                     max_width: int = 850, max_lines: int = 4):
    """Fit the complete Uthmani ayah in a balanced block; never clip words."""
    for size in (68, 64, 60, 56, 52, 48):
        font = ImageFont.truetype(font_path, size, layout_engine=ImageFont.Layout.RAQM)
        lines, current = [], ""
        for word in text.split():
            candidate = (current + " " + word).strip()
            bounds = draw.textbbox((0, 0), candidate, font=font,
                                   direction="rtl", language="ar")
            if bounds[2] - bounds[0] <= max_width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        if len(lines) <= max_lines:
            return font, lines, max(72, int(size * 1.48))
    raise ValueError("Arabic ayah does not fit safely without clipping.")


def make_frame(verse: dict, surah: int, index: int, out: Path,
               font_path: str, surah_name: str) -> None:
    if not features.check("raqm"):
        raise RuntimeError("Pillow RAQM support is required; refusing unsafe Arabic shaping.")
    _top, _bottom, accent = PALETTES[index % len(PALETTES)]
    image = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # A gentle palette-tinted veil calms the moving footage without hiding it.
    draw.rectangle((0, 0, 1080, 1920), fill=(*_top, 38))
    # Compact, centered reading panel with enough contrast for both scripts.
    draw.rounded_rectangle((76, 310, 1004, 1610), radius=54,
                           fill=(3, 12, 18, 176), outline=(*accent, 220), width=3)
    draw.rounded_rectangle((390, 355, 690, 405), radius=24,
                           fill=(*accent, 35), outline=(*accent, 150), width=2)

    title_font = ImageFont.truetype(font_path, 62, layout_engine=ImageFont.Layout.RAQM)
    draw.text((540, 455), f"سورة {surah_name}", font=title_font, fill=accent,
              anchor="mm", direction="rtl", language="ar")
    draw.line((180, 535, 900, 535), fill=(*accent, 190), width=2)

    arabic = verse.get("arabic")
    english = verse.get("english")
    if (not isinstance(arabic, str) or not arabic.strip()
            or not isinstance(english, str) or not english.strip()):
        raise ValueError("Every preview ayah needs non-empty Arabic and paired translation.")

    body_font, lines, line_height = fit_arabic_lines(draw, arabic, font_path)
    block_height = (len(lines) - 1) * line_height
    start_y = 835 - block_height / 2
    for line_index, line in enumerate(lines):
        draw.text((540, start_y + line_index * line_height), line,
                  font=body_font, fill=(255, 255, 250), anchor="mm",
                  direction="rtl", language="ar")

    # Use a true circular ayah badge instead of decorative symbols around a number.
    badge_y, badge_radius = 1135, 48
    draw.ellipse((540 - badge_radius, badge_y - badge_radius,
                  540 + badge_radius, badge_y + badge_radius),
                 fill=(*accent, 28), outline=(*accent, 255), width=4)
    number_font = ImageFont.truetype(font_path, 38, layout_engine=ImageFont.Layout.RAQM)
    ayah_no = str(verse["number"]).translate(
        str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
    )
    draw.text((540, badge_y), ayah_no, font=number_font, fill=accent,
              anchor="mm", direction="rtl", language="ar")

    draw.line((180, 1220, 900, 1220), fill=(*accent, 150), width=2)
    english_font, en_lines, english_line_height = fit_translation_lines(
        draw, english, font_path, max_width=820, max_lines=5
    )
    english_block_height = (len(en_lines) - 1) * english_line_height
    english_start_y = 1390 - english_block_height / 2
    for line_index, line in enumerate(en_lines):
        draw.text((540, english_start_y + line_index * english_line_height),
                  line, font=english_font, fill=(245, 246, 242),
                  anchor="mm")
    draw.line((300, 1535, 780, 1535), fill=(*accent, 120), width=2)
    image.save(out)

def probe(path: Path) -> dict:
    raw = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration:stream=codec_name,width,height", "-of", "json", str(path)
    ], text=True)
    data = json.loads(raw)
    video = next((s for s in data.get("streams", []) if "width" in s), None)
    audio = next((s for s in data.get("streams", []) if "codec_name" in s and "width" not in s), None)
    duration = float(data["format"]["duration"])
    if not video or (video["width"], video["height"]) != (1080, 1920):
        raise RuntimeError(f"Preview is not 1080x1920: {path}")
    if not audio or audio["codec_name"] != "mp3":
        raise RuntimeError(f"Original MP3 audio stream was not preserved: {path}")
    if duration <= 0 or duration > 65:
        raise RuntimeError(f"Preview duration outside allowed range: {duration}")
    return {"duration_seconds": round(duration, 3), "width": 1080, "height": 1920,
            "video_codec": video["codec_name"], "audio_codec": audio["codec_name"]}


def render(batch_path: Path, report_path: Path, output_dir: Path, minimum_previews: int = 2) -> dict:
    batch = json.loads(batch_path.read_text(encoding="utf-8"))
    report = json.loads(report_path.read_text(encoding="utf-8"))
    if minimum_previews < 1:
        raise ValueError("minimum_previews must be positive.")
    if batch.get("batch_status") != "review_candidates_only" or report.get("rendering_allowed") is not False:
        raise ValueError("Only review-only batch inputs are accepted.")
    if report.get("telegram_delivery") is not False or report.get("auto_publish") is not False:
        raise ValueError("Delivery and publishing must remain disabled.")
    # Validate all selected ayahs before downloading a background or loading
    # fonts. A duration-limited passage may be a shorter prefix, not the whole
    # candidate, but it must never skip or reorder ayahs.
    report_items = {x["candidate_id"]: x for x in report.get("items", [])}
    for candidate in batch.get("passages", []):
        item = report_items.get(candidate["candidate_id"])
        if not item or not item.get("status", "").startswith("audio_prepared"):
            continue
        requested = item.get("requested_verses")
        candidate_numbers = [int(v["ayah"]) for v in candidate["verses"]]
        if not isinstance(requested, list) or [int(n) for n in requested] != candidate_numbers:
            raise ValueError("Audio requested ayahs do not match the source candidate.")
        selected = item.get("selected_verses")
        if (not isinstance(selected, list) or not selected
                or [int(n) for n in selected] != candidate_numbers[:len(selected)]):
            raise ValueError("Audio-selected ayahs do not match a non-empty requested prefix.")
        if [int(n) for n in selected] != list(range(int(selected[0]), int(selected[0]) + len(selected))):
            raise ValueError("Audio-selected ayahs are not contiguous; refusing preview.")
    output_dir.mkdir(parents=True, exist_ok=True)
    font_path = font_file()
    background = output_dir / "approved_moving_background.mp4"
    download_background(APPROVED_BACKGROUND_URL, background)
    if background.stat().st_size < 100_000:
        raise RuntimeError("Approved moving background download is missing or unexpectedly small.")
    background_probe = subprocess.check_output([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=codec_name,width,height", "-of", "json", str(background)
    ], text=True)
    background_streams = json.loads(background_probe).get("streams", [])
    if not background_streams or background_streams[0].get("codec_name") not in {"h264", "hevc", "vp9", "av1"}:
        raise RuntimeError("Approved background is not a valid moving video stream.")
    report_items = {x["candidate_id"]: x for x in report.get("items", [])}
    previews = []
    for candidate in batch.get("passages", []):
        item = report_items.get(candidate["candidate_id"])
        if not item or not item.get("status", "").startswith("audio_prepared"):
            continue
        candidate_by_number = {int(v["ayah"]): v for v in candidate["verses"]}
        numbers = item.get("selected_verses")
        if not isinstance(numbers, list) or not numbers or any(int(n) not in candidate_by_number for n in numbers):
            raise ValueError("Audio-selected ayahs are missing from the source candidate; refusing preview.")
        if numbers != list(range(int(numbers[0]), int(numbers[0]) + len(numbers))):
            raise ValueError("Audio-selected ayahs are not contiguous; refusing preview.")
        verses = [candidate_by_number[int(n)] for n in numbers]
        work = output_dir / candidate["candidate_id"]
        work.mkdir(parents=True, exist_ok=True)
        segments = []
        for index, verse in enumerate(verses):
            frame = work / f"ayah_{int(verse['ayah']):03d}.png"
            surah_number = int(candidate["surah_number"])
            if not 1 <= surah_number <= len(SURAH_NAMES):
                raise ValueError(f"Invalid surah number: {surah_number}")
            make_frame({"number": int(verse["ayah"]), "arabic": verse["arabic_uthmani"],
                        "english": verse["english_saheeh_international"]},
                       surah_number, index, frame, font_path, SURAH_NAMES[surah_number - 1])
            audio = Path(item["audio_file"]).parent / f"{int(candidate['surah_number']):03d}_{int(verse['ayah']):03d}.mp3"
            if not audio.is_file():
                raise FileNotFoundError(f"Whole-ayah audio file missing: {audio}")
            segment = work / f"segment_{index:02d}.mp4"
            subprocess.run([
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                "-stream_loop", "-1", "-i", str(background), "-i", str(audio), "-i", str(frame),
                "-filter_complex",
                "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30[bg];"
                "[bg][2:v]overlay=0:0:format=auto[v]",
                "-map", "[v]", "-map", "1:a:0",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                "-pix_fmt", "yuv420p", "-c:a", "copy", "-shortest",
                "-movflags", "+faststart", str(segment)
            ], check=True)
            segments.append(segment)
        concat = work / "segments.txt"
        concat.write_text("".join(f"file '{p.resolve()}'\n" for p in segments), encoding="utf-8")
        output = output_dir / f"{candidate['candidate_id']}_REVIEW_ONLY.mp4"
        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-f", "concat", "-safe", "0", "-i", str(concat),
            "-c", "copy", "-movflags", "+faststart", str(output)
        ], check=True)
        info = probe(output)
        previews.append({
            "candidate_id": candidate["candidate_id"],
            "surah_number": int(candidate["surah_number"]),
            "verses": numbers,
            "file": str(output),
            **info,
            "review_only": True,
            "audio_approved": False,
            "rendering_approved": False,
            "telegram_delivery": False,
            "auto_publish": False,
        })
    if len(previews) < minimum_previews or len({p["surah_number"] for p in previews}) != len(previews):
        raise RuntimeError("At least two distinct-surah previews are required.")
    result = {
        "status": "review_only_previews_rendered",
        "preview_count": len(previews),
        "items": previews,
        "production_approved": False,
        "telegram_delivery": False,
        "auto_publish": False,
        "background_type": "moving_video",
        "background_source": BACKGROUND_SOURCE,
        "note": "Moving video background with transparent Arabic/English overlays. Text, translation, exact recitation, and reuse rights still require human review.",
    }
    (output_dir / "preview_report.json").write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", type=Path, required=True)
    parser.add_argument("--audio-report", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("output/quran_review_previews"))
    parser.add_argument("--minimum-previews", type=int, default=2,
                        help="Minimum number of distinct review previews required.")
    args = parser.parse_args()
    print(json.dumps(render(args.batch, args.audio_report, args.output_dir,
                            minimum_previews=args.minimum_previews), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
