"""Render strictly review-only Quran previews from selected whole-ayah audio.

Uses the curated, user-approved Pexels moving-background rotation, exact catalog
text, and original processed MP3 ayah streams. It never approves or publishes.
"""
from __future__ import annotations

import argparse
import io
import json
import subprocess
import zipfile
from datetime import datetime, timezone
import urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, features
from quran_visual_history import load_history as load_visual_history, recent_usage as recent_visual_usage

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

# Fully vocalized chapter names for the opening cover (Amiri Bold / RAQM).
SURAH_NAMES_TASHKEEL = [
    "الْفَاتِحَةِ", "الْبَقَرَةِ", "آلِ عِمْرَانَ", "النِّسَاءِ",
    "الْمَائِدَةِ", "الْأَنْعَامِ", "الْأَعْرَافِ", "الْأَنْفَالِ",
    "التَّوْبَةِ", "يُونُسَ", "هُودٍ", "يُوسُفَ", "الرَّعْدِ",
    "إِبْرَاهِيمَ", "الْحِجْرِ", "النَّحْلِ", "الْإِسْرَاءِ",
    "الْكَهْفِ", "مَرْيَمَ", "طٰهٰ", "الْأَنْبِيَاءِ", "الْحَجِّ",
    "الْمُؤْمِنُونَ", "النُّورِ", "الْفُرْقَانِ", "الشُّعَرَاءِ",
    "النَّمْلِ", "الْقَصَصِ", "الْعَنْكَبُوتِ", "الرُّومِ",
    "لُقْمَانَ", "السَّجْدَةِ", "الْأَحْزَابِ", "سَبَأَ",
    "فَاطِرٍ", "يسٓ", "الصَّافَّاتِ", "صٓ", "الزُّمَرِ",
    "غَافِرٍ", "فُصِّلَتْ", "الشُّورَىٰ", "الزُّخْرُفِ",
    "الدُّخَانِ", "الْجَاثِيَةِ", "الْأَحْقَافِ", "مُحَمَّدٍ",
    "الْفَتْحِ", "الْحُجُرَاتِ", "قٓ", "الذَّارِيَاتِ",
    "الطُّورِ", "النَّجْمِ", "الْقَمَرِ", "الرَّحْمَٰنِ",
    "الْوَاقِعَةِ", "الْحَدِيدِ", "الْمُجَادِلَةِ", "الْحَشْرِ",
    "الْمُمْتَحَنَةِ", "الصَّفِّ", "الْجُمُعَةِ", "الْمُنَافِقُونَ",
    "التَّغَابُنِ", "الطَّلَاقِ", "التَّحْرِيمِ", "الْمُلْكِ",
    "الْقَلَمِ", "الْحَاقَّةِ", "الْمَعَارِجِ", "نُوحٍ",
    "الْجِنِّ", "الْمُزَّمِّلِ", "الْمُدَّثِّرِ", "الْقِيَامَةِ",
    "الْإِنْسَانِ", "الْمُرْسَلَاتِ", "النَّبَإِ", "النَّازِعَاتِ",
    "عَبَسَ", "التَّكْوِيرِ", "الْإِنْفِطَارِ", "الْمُطَفِّفِينَ",
    "الْإِنْشِقَاقِ", "الْبُرُوجِ", "الطَّارِقِ", "الْأَعْلَىٰ",
    "الْغَاشِيَةِ", "الْفَجْرِ", "الْبَلَدِ", "الشَّمْسِ",
    "اللَّيْلِ", "الضُّحَىٰ", "الشَّرْحِ", "التِّينِ",
    "الْعَلَقِ", "الْقَدْرِ", "الْبَيِّنَةِ", "الزَّلْزَلَةِ",
    "الْعَادِيَاتِ", "الْقَارِعَةِ", "التَّكَاثُرِ", "الْعَصْرِ",
    "الْهُمَزَةِ", "الْفِيلِ", "قُرَيْشٍ", "الْمَاعُونِ",
    "الْكَوْثَرِ", "الْكَافِرُونَ", "النَّصْرِ", "الْمَسَدِ",
    "الْإِخْلَاصِ", "الْفَلَقِ", "النَّاسِ",
]
COVER_TEMPLATE_IDS = ("open_gold_brackets",)
COVER_TEMPLATE_ARCHIVE = Path("assets/background_photos/quran_cover_templates.zip")

BACKGROUND_CATALOG = Path("data/background_candidates.json")
BACKGROUND_PHOTO_MANIFEST = Path("data/background_photos_manifest.json")

INTRO_DURATION_SECONDS = 1.2
INTRO_FADE_SECONDS = 0.8

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
        ["fc-match", "-f", "%{file}", "Amiri:style=Bold"], text=True
    ).strip()
    if not result or not Path(result).is_file():
        raise RuntimeError("Amiri Bold font is required for Arabic preview rendering.")
    return result


def fit_translation_lines(draw: ImageDraw.ImageDraw, text: str, font_path: str,
                          max_width: int = 820, max_lines: int = 8):
    """Fit the complete translation in the lower text area; never truncate it.

    Long English translations can wrap to more lines and use a smaller font.
    The eight-line fallback is vertically bounded around the translation area's
    center, leaving the ayah medallion and footer divider unobstructed.
    """
    last_line_count = 0
    for size in (32, 30, 28, 26, 24, 22, 20, 18, 16):
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
        last_line_count = len(lines)
        if len(lines) <= max_lines:
            return font, lines, max(30, size + 12)
    raise ValueError(
        f"Translation needs {last_line_count} lines; it cannot fit safely "
        "inside the reserved area without clipping."
    )


def fit_arabic_lines(draw: ImageDraw.ImageDraw, text: str, font_path: str,
                     max_width: int = 850, max_lines: int = 7,
                     max_height: int = 390):
    """Fit the complete Uthmani ayah to a fixed-height area below the surah title.

    The font steps down progressively for long ayahs. Both line count and total
    block height are checked, so a wrapped ayah cannot grow upward into the
    title cartouche. No Quran words are removed or rewritten.
    """
    for size in (96, 90, 84, 78, 72, 66, 60, 56, 52, 48, 44, 40, 36, 32, 28):
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
                word_bounds = draw.textbbox((0, 0), word, font=font,
                                            direction="rtl", language="ar")
                if word_bounds[2] - word_bounds[0] > max_width:
                    raise ValueError("A Quran word is wider than the available text area.")
                current = word
        if current:
            lines.append(current)
        line_height = (max(48, int(size * 1.4)) if size <= 40
                       else max(72, int(size * 1.48)))
        block_height = max(0, len(lines) - 1) * line_height
        if len(lines) <= max_lines and block_height <= max_height:
            return font, lines, line_height
    raise ValueError(
        "Arabic ayah cannot fit safely below the surah title without clipping."
    )


def bold_font_file() -> str:
    result = subprocess.check_output(
        ["fc-match", "-f", "%{file}", "Amiri:style=Bold"], text=True
    ).strip()
    if not result or not Path(result).is_file():
        raise RuntimeError("Amiri Bold font is required for Quran title and verse numbers.")
    return result


APPROVED_DESIGN_REFERENCE = Path("references/approved_quran_design.png")


def _gold_reference_crop(reference: Image.Image, box: tuple[int, int, int, int],
                         *, clear_center: bool = False) -> Image.Image:
    """Extract only the original gold ornament pixels from the approved reference.

    The source image is resized to the renderer's exact 9:16 canvas first, so
    the extracted artwork keeps the reference's original proportions/placement.
    Background pixels are made transparent; no ornament is redrawn or guessed.
    """
    crop = reference.crop(box).convert("RGB")
    left, top, right, bottom = box
    pixels = []
    center_x, center_y = (left + right) // 2, (top + bottom) // 2
    for y in range(top, bottom):
        for x in range(left, right):
            r, g, b = crop.getpixel((x - left, y - top))
            gold_alpha = min(
                255,
                max(0, (r - g - 18) * 8),
                max(0, (g - b - 20) * 8),
                max(0, (150 - b) * 5),
            )
            if clear_center and abs(x - center_x) < 18 and abs(y - center_y) < 22:
                gold_alpha = 0
            pixels.append((r, g, b, gold_alpha))
    result = Image.new("RGBA", crop.size, (0, 0, 0, 0))
    result.putdata(pixels)
    return result


def draw_reference_surah_ornaments(image: Image.Image) -> None:
    """Composite the exact title brackets and divider pixels from the reference."""
    if not APPROVED_DESIGN_REFERENCE.is_file():
        raise FileNotFoundError(
            f"Approved Quran design reference is missing: {APPROVED_DESIGN_REFERENCE}"
        )
    with Image.open(APPROVED_DESIGN_REFERENCE) as source:
        reference = ImageOps.fit(
            source.convert("RGB"), (1080, 1920),
            method=Image.Resampling.LANCZOS
        )
    # Coordinates are on the 1080x1920 fitted reference itself.
    for box in (
        (138, 448, 270, 665),   # left open arabesque bracket
        (810, 448, 942, 665),   # right open arabesque bracket
        (298, 650, 784, 730),   # original gold floral divider
    ):
        image.alpha_composite(_gold_reference_crop(reference, box), (box[0], box[1]))


def draw_reference_ayah_medallion(image: Image.Image, ayah_number: int,
                                  font_path: str) -> None:
    """Use the exact ornate medallion from the reference, with a dynamic number."""
    if not APPROVED_DESIGN_REFERENCE.is_file():
        raise FileNotFoundError(
            f"Approved Quran design reference is missing: {APPROVED_DESIGN_REFERENCE}"
        )
    with Image.open(APPROVED_DESIGN_REFERENCE) as source:
        reference = ImageOps.fit(
            source.convert("RGB"), (1080, 1920),
            method=Image.Resampling.LANCZOS
        )
    box = (103, 846, 207, 954)
    medallion = _gold_reference_crop(reference, box, clear_center=True)
    image.alpha_composite(medallion, (box[0], box[1]))
    number_font = ImageFont.truetype(font_path, 38, layout_engine=ImageFont.Layout.RAQM)
    digits = str(ayah_number).translate(str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩"))
    draw = ImageDraw.Draw(image)
    draw.text((155, 900), digits, font=number_font, fill=(255, 196, 54, 255),
              anchor="mm", direction="rtl", language="ar",
              stroke_width=1, stroke_fill=(55, 34, 12, 170))


def fit_surah_title_font(draw: ImageDraw.ImageDraw, text: str, font_path: str,
                          center: tuple = (540, 540), max_width: int = 620,
                          max_height: int = 112):
    """Fit the complete surah title between the open ornamental brackets."""
    for size in (112, 104, 96, 88, 80, 72, 64, 56, 48):
        font = ImageFont.truetype(font_path, size, layout_engine=ImageFont.Layout.RAQM)
        bounds = draw.textbbox(center, text, font=font, anchor="mm",
                               direction="rtl", language="ar")
        if bounds[2] - bounds[0] <= max_width and bounds[3] - bounds[1] <= max_height:
            return font
    raise ValueError("Surah title cannot fit safely between its ornamental brackets.")


def make_frame(verse: dict, surah: int, index: int, out: Path,
               font_path: str, surah_name: str) -> None:
    if not features.check("raqm"):
        raise RuntimeError("Pillow RAQM support is required; refusing unsafe Arabic shaping.")
    if not isinstance(verse.get("number"), int):
        raise ValueError("Every preview ayah needs an integer verse number.")

    # Approved reference: unobstructed full-bleed scenery, bright gold title
    # between open arabesque brackets, white Quran text, gold ayah medallion,
    # and centered English translation. No panel, border, or dark overlay.
    accent = (245, 184, 55)
    image = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    title_text = f"سورة {surah_name}"
    title_center = (540, 540)
    title_font = fit_surah_title_font(draw, title_text, bold_font_file(),
                                      center=title_center)
    draw_reference_surah_ornaments(image)
    draw.text(title_center, title_text, font=title_font, fill=(*accent, 255),
              anchor="mm", direction="rtl", language="ar",
              stroke_width=2, stroke_fill=(55, 34, 12, 190))
    
    arabic = verse.get("arabic")
    english = verse.get("english")
    if (not isinstance(arabic, str) or not arabic.strip()
            or not isinstance(english, str) or not english.strip()):
        raise ValueError("Every preview ayah needs non-empty Arabic and paired translation.")

    body_font, lines, line_height = fit_arabic_lines(
        draw, arabic, font_path, max_width=850, max_lines=7, max_height=390
    )
    block_height = (len(lines) - 1) * line_height
    # Reserve a distinct lower-middle zone below the title divider.
    # Center the complete ayah block lower so even the longest wrapped ayah
    # cannot collide with the title, ornament, or English translation.
    start_y = 900 - block_height / 2
    for line_index, line in enumerate(lines):
        draw.text((600, start_y + line_index * line_height), line,
                  font=body_font, fill=(255, 255, 250, 255), anchor="mm",
                  direction="rtl", language="ar",
                  stroke_width=2, stroke_fill=(0, 0, 0, 150))

    # Exact ornate gold ayah medallion extracted from the approved reference.
    draw_reference_ayah_medallion(image, verse["number"], bold_font_file())

    english_font, en_lines, english_line_height = fit_translation_lines(
        draw, english, font_path, max_width=850, max_lines=8
    )
    english_block_height = (len(en_lines) - 1) * english_line_height
    # Match the reference's centered translation zone while keeping long Arabic
    # passages and long English translations from colliding.
    arabic_bottom = start_y + block_height / 2
    english_center_y = max(1200, arabic_bottom + 105 + english_block_height / 2)
    english_start_y = english_center_y - english_block_height / 2
    for line_index, line in enumerate(en_lines):
        draw.text((540, english_start_y + line_index * english_line_height),
                  line, font=english_font, fill=(255, 255, 245, 255),
                  anchor="mm", stroke_width=2,
                  stroke_fill=(0, 0, 0, 155))
    image.save(out)


def load_cover_template(template_index: int) -> tuple[str, Image.Image]:
    """Load one exact user-supplied cover panel from the checked-in ZIP archive."""
    if not 0 <= template_index < len(COVER_TEMPLATE_IDS):
        raise ValueError(f"Invalid cover template index: {template_index}")
    if not COVER_TEMPLATE_ARCHIVE.is_file():
        raise FileNotFoundError(
            f"User-approved four-cover archive is missing: {COVER_TEMPLATE_ARCHIVE}"
        )
    template_id = COVER_TEMPLATE_IDS[template_index]
    archive_name = f"cover_{template_id}.jpg"
    try:
        with zipfile.ZipFile(COVER_TEMPLATE_ARCHIVE) as archive:
            raw = archive.read(archive_name)
        with Image.open(io.BytesIO(raw)) as source:
            return template_id, source.convert("RGBA").copy()
    except KeyError as exc:
        raise ValueError(f"Cover template {archive_name} is missing from {COVER_TEMPLATE_ARCHIVE}") from exc
    except Exception as exc:
        raise ValueError(f"Cover template {template_id} is not a valid image: {exc}") from exc


def fit_cover_title_font(draw: ImageDraw.ImageDraw, text: str, font_path: str,
                         center: tuple = (540, 780), max_width: int = 760,
                         max_height: int = 160):
    """Fit a fully vocalized Arabic surah title inside the original circular frame."""
    for size in (118, 110, 102, 94, 86, 78, 70):
        font = ImageFont.truetype(font_path, size, layout_engine=ImageFont.Layout.RAQM)
        bounds = draw.textbbox(center, text, font=font, anchor="mm",
                               direction="rtl", language="ar")
        if bounds[2] - bounds[0] <= max_width and bounds[3] - bounds[1] <= max_height:
            return font
    raise ValueError("Fully vocalized surah title cannot fit inside the original cover frame.")


def make_intro_frame(surah_number: int, start_ayah: int, end_ayah: int,
                     out: Path, font_path: str, surah_name: str,
                     background_frame: Path | None = None,
                     cover_rotation_index: int = 0) -> str:
    """Render the approved open-bracket title over the same first scene."""
    if not features.check("raqm"):
        raise RuntimeError("Pillow RAQM support is required; refusing unsafe Arabic shaping.")
    if not 1 <= surah_number <= len(SURAH_NAMES):
        raise ValueError(f"Invalid surah number: {surah_number}")
    if start_ayah < 1 or end_ayah < start_ayah:
        raise ValueError("Opening cover needs a valid, ordered ayah range.")
    if background_frame is None or not Path(background_frame).is_file():
        raise FileNotFoundError("The opening cover requires the first full-bleed background frame.")

    with Image.open(background_frame) as source:
        image = ImageOps.fit(
            source.convert("RGB"), (1080, 1920),
            method=Image.Resampling.LANCZOS
        ).convert("RGBA")

    draw = ImageDraw.Draw(image)
    accent = (245, 184, 55)
    title_text = f"سورة {surah_name}"
    title_center = (540, 540)
    title_font = fit_surah_title_font(draw, title_text, font_path, center=title_center)
    draw_reference_surah_ornaments(image)
    draw.text(title_center, title_text, font=title_font, fill=(*accent, 255),
              anchor="mm", direction="rtl", language="ar",
              stroke_width=2, stroke_fill=(55, 34, 12, 190))
    
    digits = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
    start_text = str(start_ayah).translate(digits)
    end_text = str(end_ayah).translate(digits)
    range_text = (f"الْآيَةُ {start_text}" if start_ayah == end_ayah
                  else f"الْآيَاتُ {start_text} - {end_text}")
    range_font = ImageFont.truetype(font_path, 54, layout_engine=ImageFont.Layout.RAQM)
    draw.text((540, 840), range_text, font=range_font,
              fill=(255, 222, 142, 255), anchor="mm",
              direction="rtl", language="ar",
              stroke_width=2, stroke_fill=(35, 24, 12, 190))
    image.save(out)
    return "open_gold_brackets"

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
    if duration <= 0:
        raise RuntimeError(f"Preview has invalid duration: {duration}")
    if duration > 60.0:
        raise RuntimeError(f"Preview exceeds the absolute 60-second maximum: {duration:.3f}s")
    return {"duration_seconds": round(duration, 3), "width": 1080, "height": 1920,
            "video_codec": video["codec_name"], "audio_codec": audio["codec_name"]}


def load_approved_backgrounds(catalog_path: Path = BACKGROUND_CATALOG) -> list[dict]:
    """Return only candidates explicitly approved and download-verified in the catalog."""
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    approved = [
        item for item in catalog.get("candidates", [])
        if item.get("approved") is True
        and item.get("user_approved") is True
        and item.get("download_verified") is True
        and str(item.get("direct_video_url", "")).startswith("https://videos.pexels.com/video-files/")
    ]
    if not approved:
        raise RuntimeError("No fully verified and user-approved background candidates are available.")
    for item in approved:
        item["background_type"] = "moving_video"
    return approved


def load_approved_photo_backgrounds(manifest_path: Path = BACKGROUND_PHOTO_MANIFEST) -> list[dict]:
    """Load downloaded photo backgrounds from the separate approved photo library."""
    catalog = json.loads(manifest_path.read_text(encoding="utf-8"))
    photos = []
    for item in catalog.get("candidates", []):
        relative_path = Path(str(item.get("local_path", "")))
        if not relative_path.parts or relative_path.is_absolute() or ".." in relative_path.parts:
            continue
        path = Path.cwd() / relative_path
        if not path.is_file():
            continue
        try:
            with Image.open(path) as photo:
                photo.verify()
        except (OSError, ValueError):
            continue
        photos.append({
            "id": item["id"],
            "description": item.get("description", item["id"]),
            "source_page_url": item.get("source_page_url", ""),
            "tags": item.get("tags", []),
            "path": str(path),
            "background_type": "photo",
            "duration_seconds": None,
        })
    if not photos:
        raise RuntimeError("No downloaded photo backgrounds from data/background_photos_manifest.json are available.")
    return photos


def prepare_moving_background(candidate: dict, destination: Path) -> dict:
    """Download and validate one approved moving background before rendering."""
    download_background(candidate["direct_video_url"], destination)
    if destination.stat().st_size < 100_000:
        raise RuntimeError(f"Background download is missing or unexpectedly small: {candidate['id']}")
    raw = subprocess.check_output([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "format=duration:stream=codec_name,width,height", "-of", "json", str(destination)
    ], text=True)
    metadata = json.loads(raw)
    streams = metadata.get("streams", [])
    if not streams or streams[0].get("codec_name") not in {"h264", "hevc", "vp9", "av1"}:
        raise RuntimeError(f"Background is not a valid moving video stream: {candidate['id']}")
    duration = float(metadata.get("format", {}).get("duration") or candidate.get("duration_seconds") or 0)
    if duration <= 0:
        raise RuntimeError(f"Background duration could not be verified: {candidate['id']}")
    return {
        "id": candidate["id"],
        "duration_seconds": round(duration, 3),
        "description": candidate.get("description", candidate["id"]),
        "source_page_url": candidate.get("source_page_url", ""),
        "codec": streams[0].get("codec_name"),
        "width": streams[0].get("width"),
        "height": streams[0].get("height"),
    }



def photo_motion_filter() -> str:
    """Apply a smooth centered 0–30% zoom cycle to every background type."""
    return (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        "zoompan=z='1.15-0.15*cos(2*PI*on/360)':"
        "x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':"
        "d=1:s=1080x1920:fps=30,setsar=1[bg];"
    )


def audio_duration_seconds(path: Path) -> float:
    """Return the measured duration of one ayah audio file; zero means probe unavailable."""
    try:
        raw = subprocess.check_output([
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(path)
        ], text=True)
        duration = float(raw.strip())
        return duration if duration > 0 else 0.0
    except (OSError, subprocess.SubprocessError, ValueError):
        # A missing/failed probe must never stop a review preview. The renderer
        # falls back to the longest verified approved background.
        return 0.0


def background_categories(item: dict) -> set[str]:
    """Return normalized visual categories for one approved background."""
    tags = item.get("tags", [])
    if not isinstance(tags, list):
        return set()
    return {str(tag).strip().lower() for tag in tags if isinstance(tag, str) and tag.strip()}


def choose_first_background(backgrounds: list[dict], start_index: int,
                            recent_ids: set[str], recent_categories: set[str]) -> dict:
    """Rotate deterministically while preferring assets and categories absent from recent posts."""
    if not backgrounds:
        raise ValueError("At least one approved background is required.")
    start = start_index % len(backgrounds)
    rotated = backgrounds[start:] + backgrounds[:start]
    return min(
        rotated,
        key=lambda item: (
            item["id"] in recent_ids,
            len(background_categories(item) & recent_categories),
            rotated.index(item),
        ),
    )


def choose_cover_template(rotation_index: int, recent_cover_ids: set[str]) -> tuple[str, int]:
    """Choose the next cover template not used by the recent delivered posts."""
    for offset in range(len(COVER_TEMPLATE_IDS)):
        index = (rotation_index + offset) % len(COVER_TEMPLATE_IDS)
        template_id = COVER_TEMPLATE_IDS[index]
        if template_id not in recent_cover_ids:
            return template_id, index
    index = rotation_index % len(COVER_TEMPLATE_IDS)
    return COVER_TEMPLATE_IDS[index], index


def choose_background_for_ayah(backgrounds: list[dict], audio_duration: float,
                                used_ids: set[str] | None = None,
                                avoid_categories: set[str] | None = None) -> dict:
    """Choose an unused, category-diverse asset long enough for this ayah when possible."""
    if not backgrounds:
        raise ValueError("At least one approved background is required.")
    used_ids = used_ids or set()
    avoid_categories = avoid_categories or set()
    available = [item for item in backgrounds if item["id"] not in used_ids]
    if not available:
        available = list(backgrounds)
    if audio_duration > 0:
        suitable = [
            item for item in available
            if item.get("background_type") == "photo"
            or float(item.get("duration_seconds") or 0) >= audio_duration
        ]
        pool = suitable or [item for item in available if item.get("background_type") != "photo"]
        if not pool:
            pool = available
        if not suitable:
            best_duration = max(float(item.get("duration_seconds") or 0) for item in pool)
            pool = [item for item in pool if float(item.get("duration_seconds") or 0) == best_duration]
    else:
        pool = available
    diverse = [item for item in pool if not (background_categories(item) & avoid_categories)]
    return (diverse or pool)[0]


def build_scene_transition_filter(segment_durations: list[float],
                                  transition_seconds: float = 0.35,
                                  target_duration: float | None = None) -> tuple[str, float]:
    """Build video-only crossfades and pad/trim video to the exact original audio duration."""
    if len(segment_durations) < 2:
        raise ValueError("At least two segments are required for scene transitions.")
    if transition_seconds <= 0 or any(duration <= transition_seconds for duration in segment_durations):
        raise ValueError("Every segment must be longer than the positive transition duration.")
    total_duration = sum(segment_durations) if target_duration is None else float(target_duration)
    if total_duration <= 0:
        raise ValueError("Target duration must be positive.")
    filters = [
        f"[{index}:v]settb=AVTB,setpts=PTS-STARTPTS,fps=30,format=yuv420p[v{index}]"
        for index in range(len(segment_durations))
    ]
    current = "v0"
    cumulative_duration = segment_durations[0]
    for index in range(1, len(segment_durations)):
        next_label = f"xfade{index}"
        offset = cumulative_duration - transition_seconds
        filters.append(
            f"[{current}][v{index}]xfade=transition=fade:duration={transition_seconds:g}:"
            f"offset={offset:.6f}[{next_label}]"
        )
        current = next_label
        cumulative_duration += segment_durations[index] - transition_seconds
    overlap = transition_seconds * (len(segment_durations) - 1)
    crossfaded_duration = sum(segment_durations) - overlap
    padding = max(0.0, total_duration - crossfaded_duration)
    filters.append(
        f"[{current}]tpad=stop_mode=clone:stop_duration={padding:g},"
        f"trim=duration={total_duration:.6f},setpts=PTS-STARTPTS[vout]"
    )
    return ";".join(filters), total_duration


def media_duration_seconds(path: Path) -> float:
    """Measure the muxed audio-only MP3 duration; zero means ffprobe could not verify it."""
    try:
        raw = subprocess.check_output([
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(path),
        ], text=True)
        duration = float(raw.strip())
        return duration if duration > 0 else 0.0
    except (OSError, subprocess.SubprocessError, ValueError):
        return 0.0


def assemble_review_segments(segments: list[Path], audio_files: list[Path],
                             concat_path: Path, output_path: Path, work_dir: Path) -> dict:
    """Crossfade video only; concatenate the source MP3 files directly with stream copy."""
    concat_path.write_text(
        "".join(f"file '{segment.resolve()}'\n" for segment in segments),
        encoding="utf-8",
    )
    if len(segments) == 1:
        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-f", "concat", "-safe", "0", "-i", str(concat_path),
            "-c", "copy", "-movflags", "+faststart", str(output_path),
        ], check=True)
        return {"transition": "none_single_scene", "transition_seconds": 0.0, "scene_count": 1}
    if len(audio_files) != len(segments) or not audio_files:
        raise ValueError("Every rendered scene must have its matching original MP3 audio file.")
    durations = [probe(segment)["duration_seconds"] for segment in segments]
    audio_concat_path = work_dir / "audio_segments.txt"
    audio_concat_path.write_text(
        "".join(f"file '{audio.resolve()}'\n" for audio in audio_files),
        encoding="utf-8",
    )
    audio_path = work_dir / "joined_original_audio.mp3"
    silent_video_path = work_dir / "crossfaded_video_only.mp4"
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-f", "concat", "-safe", "0", "-i", str(audio_concat_path),
        "-c:a", "copy", str(audio_path),
    ], check=True)
    measured_audio_duration = media_duration_seconds(audio_path)
    target_duration = measured_audio_duration or sum(durations)
    filter_complex, total_duration = build_scene_transition_filter(
        durations, target_duration=target_duration,
    )
    video_command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]
    for segment in segments:
        video_command.extend(["-i", str(segment)])
    video_command.extend([
        "-filter_complex", filter_complex,
        "-map", "[vout]", "-an",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
        "-pix_fmt", "yuv420p", "-t", f"{total_duration:.6f}",
        str(silent_video_path),
    ])
    subprocess.run(video_command, check=True)
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(silent_video_path), "-i", str(audio_path),
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "copy", "-c:a", "copy",
        "-movflags", "+faststart", str(output_path),
    ], check=True)
    return {
        "transition": "video_only_crossfade",
        "transition_seconds": 0.35,
        "scene_count": len(segments),
        "audio_stream": "original_mp3_stream_copy",
        "audio_reencoded": False,
        "duration_target_seconds": round(total_duration, 3),
        "video_overlap_padding_seconds": round(max(0.0, total_duration - (sum(durations) - 0.35 * (len(segments) - 1))), 3),
    }

def render(batch_path: Path, report_path: Path, output_dir: Path, minimum_previews: int = 2, background_rotation_index: int = 0, visual_history_path: Path | None = None) -> dict:
    batch = json.loads(batch_path.read_text(encoding="utf-8"))
    report = json.loads(report_path.read_text(encoding="utf-8"))
    if minimum_previews < 1:
        raise ValueError("minimum_previews must be positive.")
    if background_rotation_index < 0:
        raise ValueError("background_rotation_index must be non-negative.")
    if batch.get("batch_status") != "review_candidates_only" or report.get("rendering_allowed") is not False:
        raise ValueError("Only review-only batch inputs are accepted.")
    if report.get("telegram_delivery") is not False or report.get("auto_publish") is not False:
        raise ValueError("Delivery and publishing must remain disabled.")
    # Validate all selected ayahs before rendering. Ordinary videos remain <=45s;
    # only one complete ayah may use the exceptional <=60s allowance.
    candidates = {x["candidate_id"]: x for x in batch.get("passages", [])}
    report_items = report.get("items", [])
    for item in report_items:
        if not item.get("status", "").startswith("audio_prepared"):
            continue
        source_candidate_id = item.get("source_candidate_id", item["candidate_id"])
        candidate = candidates.get(source_candidate_id)
        if not candidate:
            raise ValueError("Audio part references a missing source candidate.")
        requested = item.get("requested_verses")
        candidate_numbers = [int(v["ayah"]) for v in candidate["verses"]]
        if not isinstance(requested, list) or [int(n) for n in requested] != candidate_numbers:
            raise ValueError("Audio requested ayahs do not match the source candidate.")
        selected = item.get("selected_verses")
        start = candidate_numbers.index(int(selected[0])) if isinstance(selected, list) and selected and int(selected[0]) in candidate_numbers else -1
        if (start < 0 or [int(n) for n in selected] != candidate_numbers[start:start + len(selected)]):
            raise ValueError("Audio-selected ayahs do not match a contiguous requested slice.")
        if start != 0:
            raise ValueError("Preview must select the opening contiguous prefix of the requested ayahs.")
        audio_duration = item.get("duration_seconds")
        exceptional_single_ayah = len(selected) == 1 and isinstance(audio_duration, (int, float)) and 45.0 < audio_duration <= 60.0
        allowed_seconds = 60.0 if exceptional_single_ayah else 45.0
        if not isinstance(audio_duration, (int, float)) or audio_duration <= 0 or audio_duration > allowed_seconds:
            raise ValueError(f"Prepared audio exceeds the {allowed_seconds:g}-second duration policy for its selected ayah count.")
    output_dir.mkdir(parents=True, exist_ok=True)
    font_path = font_file()
    moving_backgrounds = load_approved_backgrounds()
    photo_backgrounds = load_approved_photo_backgrounds()
    visual_history_path = visual_history_path or Path("data/quran_visual_history.json")
    visual_history = load_visual_history(visual_history_path)
    recent_background_ids, recent_background_categories, recent_cover_ids = recent_visual_usage(visual_history)
    # Interleave the two libraries so a multi-ayah preview naturally uses
    # both moving footage and still photography instead of exhausting one pool.
    approved_backgrounds = []
    for index in range(max(len(moving_backgrounds), len(photo_backgrounds))):
        if index < len(moving_backgrounds):
            approved_backgrounds.append(moving_backgrounds[index])
        if index < len(photo_backgrounds):
            approved_backgrounds.append(photo_backgrounds[index])
    prepared_backgrounds = {}
    previews = []
    for item in report_items:
        if not item.get("status", "").startswith("audio_prepared"):
            continue
        source_candidate_id = item.get("source_candidate_id", item["candidate_id"])
        candidate = candidates[source_candidate_id]
        candidate_by_number = {int(v["ayah"]): v for v in candidate["verses"]}
        numbers = item.get("selected_verses")
        if not isinstance(numbers, list) or not numbers or any(int(n) not in candidate_by_number for n in numbers):
            raise ValueError("Audio-selected ayahs are missing from the source candidate; refusing preview.")
        if numbers != list(range(int(numbers[0]), int(numbers[0]) + len(numbers))):
            raise ValueError("Audio-selected ayahs are not contiguous; refusing preview.")
        verses = [candidate_by_number[int(n)] for n in numbers]
        part_id = item["candidate_id"]
        work = output_dir / part_id
        work.mkdir(parents=True, exist_ok=True)
        # Rotate across the combined video+photo pool. The run-specific index
        # is supplied by GitHub Actions so consecutive Cron dispatches do not
        # keep starting at the same daily time slot.
        rotation_start = (background_rotation_index + len(previews)) % len(approved_backgrounds)
        first_background = choose_first_background(
            approved_backgrounds, rotation_start,
            recent_background_ids, recent_background_categories,
        )
        remaining_videos = sorted(
            (
                candidate for candidate in approved_backgrounds
                if candidate["id"] != first_background["id"]
                and candidate.get("background_type") != "photo"
            ),
            key=lambda candidate: float(candidate.get("duration_seconds") or 0),
            reverse=True,
        )
        remaining_photos = [
            candidate for candidate in approved_backgrounds
            if candidate["id"] != first_background["id"]
            and candidate.get("background_type") == "photo"
        ]
        # Put the other media type next, guaranteeing a mixed look even
        # in short passages; continue alternating after that.
        next_pool, later_pool = (
            (remaining_photos, remaining_videos)
            if first_background.get("background_type") != "photo"
            else (remaining_videos, remaining_photos)
        )
        remaining_backgrounds = []
        for background_index in range(max(len(next_pool), len(later_pool))):
            if background_index < len(next_pool):
                remaining_backgrounds.append(next_pool[background_index])
            if background_index < len(later_pool):
                remaining_backgrounds.append(later_pool[background_index])
        background_sequence = [first_background] + remaining_backgrounds
        used_backgrounds = []
        segments = []
        audio_files = []
        used_background_ids = set()
        used_background_categories = set()
        for index, verse in enumerate(verses):
            processed_audio = item.get("processed_audio_files", {}).get(str(int(verse["ayah"])))
            audio = (Path(processed_audio) if processed_audio else
                     Path(item["audio_file"]).parent / f"{int(candidate['surah_number']):03d}_{int(verse['ayah']):03d}.mp3")
            if not audio.is_file():
                raise FileNotFoundError(f"Whole-ayah audio file missing: {audio}")
            ayah_audio_duration = audio_duration_seconds(audio)
            background_candidate = choose_background_for_ayah(
                background_sequence, ayah_audio_duration, used_background_ids,
                recent_background_categories | used_background_categories,
            )
            used_background_ids.add(background_candidate["id"])
            used_background_categories.update(background_categories(background_candidate))
            if background_candidate["id"] not in prepared_backgrounds:
                if background_candidate.get("background_type") == "photo":
                    prepared_backgrounds[background_candidate["id"]] = {
                        "id": background_candidate["id"],
                        "description": background_candidate.get("description", background_candidate["id"]),
                        "source_page_url": background_candidate.get("source_page_url", ""),
                        "tags": background_candidate.get("tags", []),
                        "path": background_candidate["path"],
                        "background_type": "photo",
                        "width": None,
                        "height": None,
                    }
                else:
                    bg_path = output_dir / "background_assets" / f'{background_candidate["id"]}.mp4'
                    bg_path.parent.mkdir(parents=True, exist_ok=True)
                    prepared_backgrounds[background_candidate["id"]] = prepare_moving_background(
                        background_candidate, bg_path
                    )
                    prepared_backgrounds[background_candidate["id"]]["path"] = str(bg_path)
                    prepared_backgrounds[background_candidate["id"]]["background_type"] = "moving_video"
                    prepared_backgrounds[background_candidate["id"]]["tags"] = background_candidate.get("tags", [])
            background = Path(prepared_backgrounds[background_candidate["id"]]["path"])
            used_backgrounds.append(prepared_backgrounds[background_candidate["id"]])
            frame = work / f"ayah_{int(verse['ayah']):03d}.png"
            surah_number = int(candidate["surah_number"])
            if not 1 <= surah_number <= len(SURAH_NAMES):
                raise ValueError(f"Invalid surah number: {surah_number}")
            make_frame({"number": int(verse["ayah"]), "arabic": verse["arabic_uthmani"],
                        "english": verse["english_saheeh_international"]},
                       surah_number, index, frame, font_path, SURAH_NAMES[surah_number - 1])
            segment = work / f"segment_{index:02d}.mp4"
            background_input = (
                ["-loop", "1", "-framerate", "30", "-i", str(background)]
                if background_candidate.get("background_type") == "photo"
                else ["-stream_loop", "-1", "-i", str(background)]
            )
            command = [
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                *background_input, "-i", str(audio), "-i", str(frame),
            ]
            if index == 0:
                # The opening title is an overlay on the first ayah segment.
                # It adds no silent lead-in and does not change the audio stream.
                intro = work / "opening_cover.png"
                cover_background = work / "opening_background.png"
                if background_candidate.get("background_type") == "photo":
                    with Image.open(background) as source_photo:
                        ImageOps.fit(source_photo.convert("RGB"), (1080, 1920)).save(cover_background)
                else:
                    subprocess.run([
                        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                        "-ss", "0", "-i", str(background), "-frames:v", "1",
                        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
                        str(cover_background),
                    ], check=True)
                scheduled_cover_index = (background_rotation_index + len(previews)) % len(COVER_TEMPLATE_IDS)
                cover_template_id, cover_rotation_index = choose_cover_template(
                    scheduled_cover_index, recent_cover_ids,
                )
                make_intro_frame(
                    surah_number, int(numbers[0]), int(numbers[-1]),
                    intro, font_path, SURAH_NAMES[surah_number - 1],
                    background_frame=cover_background,
                    cover_rotation_index=cover_rotation_index,
                )
                command.extend(["-loop", "1", "-framerate", "30", "-i", str(intro)])
                background_filter = (
                    photo_motion_filter()
                )
                fade_start = INTRO_DURATION_SECONDS - INTRO_FADE_SECONDS
                fade_start_text = f"{fade_start:g}"
                fade_duration_text = f"{INTRO_FADE_SECONDS:g}"
                filter_complex = background_filter + (
                    # Composite the first ayah from t=0 beneath the full-screen cover.
                    # Fade only the cover's alpha channel to reveal the live background
                    # and first ayah smoothly; the original recitation remains untouched.
                    "[bg][2:v]overlay=0:0:format=auto[ayah];"
                    f"[3:v]format=rgba,fade=t=out:st={fade_start_text}:"
                    f"d={fade_duration_text}:alpha=1[intro];"
                    "[ayah][intro]overlay=0:0:format=auto[v]"
                )
            else:
                background_filter = (
                    photo_motion_filter()
                )
                filter_complex = background_filter + "[bg][2:v]overlay=0:0:format=auto[v]"
            command.extend([
                "-filter_complex", filter_complex,
                "-map", "[v]", "-map", "1:a:0",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-maxrate", "6M", "-bufsize", "12M",
                "-pix_fmt", "yuv420p", "-c:a", "copy", "-shortest",
                "-movflags", "+faststart", str(segment)
            ])
            subprocess.run(command, check=True)
            segments.append(segment)
            audio_files.append(audio)
        concat = work / "segments.txt"
        output = output_dir / f"{part_id}_REVIEW_ONLY.mp4"
        transition_info = assemble_review_segments(segments, audio_files, concat, output, work)
        info = probe(output)
        preview_limit = 60.0 if len(verses) == 1 and float(item.get("duration_seconds", 0)) > 45.0 else 45.0
        if info["duration_seconds"] > preview_limit:
            raise RuntimeError(f"Rendered preview exceeds the {preview_limit:g}-second duration policy for its selected ayah count: {info['duration_seconds']:.3f}s")
        previews.append({
            "candidate_id": part_id,
            "source_candidate_id": source_candidate_id,
            "part_index": int(item.get("part_index", 1)),
            "part_count": int(item.get("part_count", 1)),
            "surah_number": int(candidate["surah_number"]),
            "verses": numbers,
            "background": used_backgrounds[0],
            "background_sequence": used_backgrounds,
            "background_categories": sorted(set().union(*(background_categories(x) for x in used_backgrounds))),
            "cover_template_id": cover_template_id,
            "visual_transition": transition_info,
            "cover_rotation_index": cover_rotation_index,
            "file": str(output),
            **info,
            "review_only": True,
            "audio_approved": False,
            "rendering_approved": False,
            "telegram_delivery": False,
            "auto_publish": False,
        })
    if len(previews) < minimum_previews:
        raise RuntimeError(f"At least {minimum_previews} review previews are required.")
    result = {
        "status": "review_only_previews_rendered",
        "preview_count": len(previews),
        "items": previews,
        "production_approved": False,
        "telegram_delivery": False,
        "auto_publish": False,
        "background_type": "mixed_moving_video_and_photo",
        "background_source": "Approved Pexels moving-video catalog plus downloaded photo manifest",
        "background_library_counts": {
            "moving_video": len(moving_backgrounds),
            "photo": len(photo_backgrounds),
            "combined": len(approved_backgrounds),
        },
        "background_rotation": [prepared_backgrounds[k] for k in prepared_backgrounds],
        "background_rotation_enabled": True,
        "background_rotation_start_index": background_rotation_index % len(approved_backgrounds),
        "cover_rotation_enabled": True,
        "cover_rotation_count": len(COVER_TEMPLATE_IDS),
        "cover_rotation_start_index": background_rotation_index % len(COVER_TEMPLATE_IDS),
        "visual_history_source": str(visual_history_path),
        "cross_video_background_history_enabled": True,
        "recent_background_history_window": 6,
        "recent_cover_history_window": 3,
        "scene_transition": {"type": "video_only_crossfade", "duration_seconds": 0.35, "audio_reencoded": False},
        "opening_cover": {"included_in_video": True, "duration_seconds": INTRO_DURATION_SECONDS, "fade_seconds": INTRO_FADE_SECONDS, "fade_start_seconds": INTRO_DURATION_SECONDS - INTRO_FADE_SECONDS, "ayah_visible_from_seconds": 0, "audio_starts_at_seconds": 0, "visible_only_at_start": True, "transition": "alpha_fade_to_first_ayah", "template_count": len(COVER_TEMPLATE_IDS), "title_font": "Amiri Bold", "title_vocalization": "full_tashkeel"},
        "note": "One of the four original user-supplied covers is selected by the monotonic GitHub run rotation; the surah name is fully vocalized and rendered with Amiri Bold. The first ayah is composited from t=0 beneath the cover; the cover fades out over 0.8 seconds beginning at 0.4 seconds, revealing the ayah and moving background smoothly. Original recitation starts at t=0 and the video remains review-only.",
    }
    (output_dir / "preview_report.json").write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    return result


def scheduled_background_rotation_index(now: datetime, background_count: int) -> int:
    """Choose a daily slot across every approved background, regardless of catalog size."""
    if background_count < 1:
        raise ValueError("At least one approved background is required.")
    slot = {3: 0, 11: 1, 17: 2}.get(now.hour, now.hour % 3)
    return (int(now.strftime("%j")) * 3 + slot) % background_count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", type=Path, required=True)
    parser.add_argument("--audio-report", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("output/quran_review_previews"))
    parser.add_argument("--minimum-previews", type=int, default=2,
                        help="Minimum number of distinct review previews required.")
    parser.add_argument("--background-rotation-index", type=int, default=None,
                        help="Starting index for the approved background rotation; defaults to a daily UTC schedule slot.")
    parser.add_argument("--visual-history", type=Path, default=Path("data/quran_visual_history.json"),
                        help="Persistent visual history updated only after confirmed Telegram delivery.")
    args = parser.parse_args()
    rotation_index = args.background_rotation_index
    if rotation_index is None:
        now = datetime.now(timezone.utc)
        total_backgrounds = len(load_approved_backgrounds()) + len(load_approved_photo_backgrounds())
        rotation_index = scheduled_background_rotation_index(now, total_backgrounds)
    print(json.dumps(render(args.batch, args.audio_report, args.output_dir,
                            minimum_previews=args.minimum_previews,
                            background_rotation_index=rotation_index,
                            visual_history_path=args.visual_history), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
