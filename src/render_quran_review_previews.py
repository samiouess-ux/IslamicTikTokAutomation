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


def make_frame(verse: dict, surah: int, index: int, out: Path, font_path: str, surah_name: str) -> None:
    if not features.check("raqm"):
        raise RuntimeError("Pillow RAQM support is required; refusing unsafe Arabic shaping.")
    top, bottom, accent = PALETTES[index % len(PALETTES)]
    # Transparent text/decorative layer: the moving stock video remains visible underneath.
    image = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((64, 250, 1016, 1570), radius=42,
                           fill=(0, 0, 0, 72), outline=(*accent, 235), width=3)
    draw.line((170, 390, 910, 390), fill=(*accent, 220), width=2)
    draw.line((170, 1500, 910, 1500), fill=(*accent, 220), width=2)
    title_font = ImageFont.truetype(font_path, 54, layout_engine=ImageFont.Layout.RAQM)
    body_font = ImageFont.truetype(font_path, 66, layout_engine=ImageFont.Layout.RAQM)
    number_font = ImageFont.truetype(font_path, 38, layout_engine=ImageFont.Layout.RAQM)
    english_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
    draw.text((540, 320), f"سورة {surah_name}", font=title_font, fill=accent,
              anchor="mm", direction="rtl", language="ar")
    arabic = verse.get("arabic")
    english = verse.get("english")
    if not isinstance(arabic, str) or not arabic.strip() or not isinstance(english, str) or not english.strip():
        raise ValueError("Every preview ayah needs non-empty Arabic and paired translation.")
    # Wrap Arabic without deleting, normalizing, or rewriting any characters.
    lines, current = [], ""
    for word in arabic.split():
        candidate = (current + " " + word).strip()
        if draw.textbbox((0, 0), candidate, font=body_font, direction="rtl", language="ar")[2] <= 820:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    if len(lines) > 6:
        raise ValueError(f"Arabic ayah {verse['number']} does not fit; refusing to clip.")
    line_h = 112
    start_y = 790 - (len(lines)-1)*line_h/2
    for i, line in enumerate(lines):
        draw.text((540, start_y+i*line_h), line, font=body_font, fill=(255,255,248),
                  anchor="mm", direction="rtl", language="ar")
    ayah_no = str(verse["number"]).translate(str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩"))
    draw.text((540, 1120), f"۞ {ayah_no} ۞", font=number_font, fill=accent,
              anchor="mm", direction="rtl", language="ar")
    # Translation is wrapped separately; all source words are retained.
    en_lines, current = [], ""
    for word in english.split():
        candidate = (current + " " + word).strip()
        if draw.textbbox((0,0), candidate, font=english_font)[2] <= 820:
            current = candidate
        else:
            if current:
                en_lines.append(current)
            current = word
    if current:
        en_lines.append(current)
    if len(en_lines) > 5:
        raise ValueError(f"Translation for ayah {verse['number']} does not fit; refusing to clip.")
    y = 1320 - (len(en_lines)-1)*48/2
    for line in en_lines:
        draw.text((540, y), line, font=english_font, fill=(245,245,239), anchor="mm")
        y += 48
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


def render(batch_path: Path, report_path: Path, output_dir: Path) -> dict:
    batch = json.loads(batch_path.read_text(encoding="utf-8"))
    report = json.loads(report_path.read_text(encoding="utf-8"))
    if batch.get("batch_status") != "review_candidates_only" or report.get("rendering_allowed") is not False:
        raise ValueError("Only review-only batch inputs are accepted.")
    if report.get("telegram_delivery") is not False or report.get("auto_publish") is not False:
        raise ValueError("Delivery and publishing must remain disabled.")
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
        verses = candidate["verses"]
        numbers = [int(v["ayah"]) for v in verses]
        if item.get("selected_verses") != numbers:
            raise ValueError("Audio and exact ayah list do not match; refusing preview.")
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
    if len(previews) < 2 or len({p["surah_number"] for p in previews}) != len(previews):
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
    args = parser.parse_args()
    print(json.dumps(render(args.batch, args.audio_report, args.output_dir), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
