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
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, features

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

INTRO_DURATION_SECONDS = 1.6
INTRO_FADE_SECONDS = 0.4

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
                          max_width: int = 820, max_lines: int = 5):
    """Fit every translation word by reducing font size; never truncate text."""
    for size in (32, 30, 28, 26, 24, 22):
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
    for size in (96, 90, 84, 78, 72, 66, 60, 56, 52, 48):
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


def bold_font_file() -> str:
    result = subprocess.check_output(
        ["fc-match", "-f", "%{file}", "Amiri:style=Bold"], text=True
    ).strip()
    if not result or not Path(result).is_file():
        raise RuntimeError("Amiri Bold font is required for Quran title and verse numbers.")
    return result


def draw_surah_cartouche(draw: ImageDraw.ImageDraw, accent: tuple,
                         center_x: int = 540, center_y: int = 465) -> None:
    """Draw a restrained double-line Islamic cartouche around the surah title."""
    outer = [
        (center_x, center_y - 72), (center_x + 28, center_y - 54),
        (center_x + 238, center_y - 54), (center_x + 270, center_y - 34),
        (center_x + 292, center_y), (center_x + 270, center_y + 34),
        (center_x + 238, center_y + 54), (center_x + 28, center_y + 54),
        (center_x, center_y + 72), (center_x - 28, center_y + 54),
        (center_x - 238, center_y + 54), (center_x - 270, center_y + 34),
        (center_x - 292, center_y), (center_x - 270, center_y - 34),
        (center_x - 238, center_y - 54), (center_x - 28, center_y - 54),
    ]
    inner = [
        (center_x, center_y - 59), (center_x + 24, center_y - 43),
        (center_x + 232, center_y - 43), (center_x + 255, center_y - 28),
        (center_x + 273, center_y), (center_x + 255, center_y + 28),
        (center_x + 232, center_y + 43), (center_x + 24, center_y + 43),
        (center_x, center_y + 59), (center_x - 24, center_y + 43),
        (center_x - 232, center_y + 43), (center_x - 255, center_y + 28),
        (center_x - 273, center_y), (center_x - 255, center_y - 28),
        (center_x - 232, center_y - 43), (center_x - 24, center_y - 43),
    ]
    draw.line(outer + [outer[0]], fill=(*accent, 230), width=3, joint="curve")
    draw.line(inner + [inner[0]], fill=(*accent, 115), width=2, joint="curve")
    for x in (center_x - 292, center_x + 292):
        draw.ellipse((x - 8, center_y - 8, x + 8, center_y + 8),
                     outline=(*accent, 220), width=2)
        draw.ellipse((x - 2, center_y - 2, x + 2, center_y + 2),
                     fill=(*accent, 220))


def make_frame(verse: dict, surah: int, index: int, out: Path,
               font_path: str, surah_name: str) -> None:
    if not features.check("raqm"):
        raise RuntimeError("Pillow RAQM support is required; refusing unsafe Arabic shaping.")
    palette_index = (surah * 7 + int(verse.get("number", index + 1)) * 3 + index) % len(PALETTES)
    _top, _bottom, accent = PALETTES[palette_index]
    image = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Calm the approved moving footage while leaving the scenery visible.
    draw.rectangle((0, 0, 1080, 1920), fill=(*_top, 30))
    # A slimmer, lighter reading panel gives the footage more room and avoids
    # the oversized opaque-card appearance of the first preview.
    draw.rounded_rectangle((82, 320, 998, 1600), radius=48,
                           fill=(3, 12, 18, 148), outline=(*accent, 175), width=2)
    draw.rounded_rectangle((94, 332, 986, 1588), radius=40,
                           outline=(*accent, 55), width=1)

    title_font = ImageFont.truetype(bold_font_file(), 68, layout_engine=ImageFont.Layout.RAQM)
    draw_surah_cartouche(draw, accent)
    draw.text((540, 465), f"سورة {surah_name}", font=title_font, fill=accent,
              anchor="mm", direction="rtl", language="ar")
    draw.line((210, 575, 870, 575), fill=(*accent, 155), width=2)
    draw.polygon([(540, 568), (547, 575), (540, 582), (533, 575)],
                 fill=(*accent, 190))

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
                  font=body_font, fill=(255, 255, 250, 255), anchor="mm",
                  direction="rtl", language="ar")

    # The verse number remains a separate gold circular medallion.
    badge_y, badge_radius = 1135, 49
    draw.ellipse((540 - badge_radius, badge_y - badge_radius,
                  540 + badge_radius, badge_y + badge_radius),
                 fill=(*accent, 25), outline=(*accent, 245), width=4)
    draw.ellipse((540 - badge_radius + 8, badge_y - badge_radius + 8,
                  540 + badge_radius - 8, badge_y + badge_radius - 8),
                 outline=(*accent, 115), width=2)
    number_font = ImageFont.truetype(bold_font_file(), 40, layout_engine=ImageFont.Layout.RAQM)
    ayah_no = str(verse["number"]).translate(
        str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
    )
    draw.text((540, badge_y), ayah_no, font=number_font, fill=accent,
              anchor="mm", direction="rtl", language="ar")

    draw.line((210, 1220, 870, 1220), fill=(*accent, 135), width=2)
    english_font, en_lines, english_line_height = fit_translation_lines(
        draw, english, font_path, max_width=820, max_lines=5
    )
    english_block_height = (len(en_lines) - 1) * english_line_height
    english_start_y = 1390 - english_block_height / 2
    for line_index, line in enumerate(en_lines):
        draw.text((540, english_start_y + line_index * english_line_height),
                  line, font=english_font, fill=(248, 249, 246, 255),
                  anchor="mm")
    draw.line((330, 1535, 750, 1535), fill=(*accent, 105), width=2)
    image.save(out)


def make_intro_frame(surah_number: int, start_ayah: int, end_ayah: int,
                     out: Path, font_path: str, surah_name: str) -> None:
    """Render the user's ornate emerald-marble and gold-medallion reference cover."""
    if not features.check("raqm"):
        raise RuntimeError("Pillow RAQM support is required; refusing unsafe Arabic shaping.")
    if not 1 <= surah_number <= len(SURAH_NAMES):
        raise ValueError(f"Invalid surah number: {surah_number}")
    if start_ayah < 1 or end_ayah < start_ayah:
        raise ValueError("Opening cover needs a valid, ordered ayah range.")

    import math
    width, height = 1080, 1920

    # Layered emerald stone texture with irregular mineral veins.
    noise = Image.effect_noise((540, 960), 52).resize(
        (width, height), Image.Resampling.BICUBIC
    )
    marble = ImageOps.colorize(noise, black="#000d0b", white="#24634b").convert("RGBA")
    shade = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    shade_draw = ImageDraw.Draw(shade)
    for y in range(height):
        edge = abs(y - height / 2) / (height / 2)
        shade_draw.line((0, y, width, y), fill=(0, 0, 0, int(20 + 45 * edge)))
    image = Image.alpha_composite(marble, shade)

    veins = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    vd = ImageDraw.Draw(veins)
    for idx, (sx, phase, amp) in enumerate(((-90, .2, 115), (80, 1.8, 65),
                                             (1020, 2.7, 100), (1180, 4.1, 80))):
        pts = []
        for step in range(161):
            y = step * (height - 1) / 160
            x = sx + amp * math.sin(step / 17 + phase) + 22 * math.sin(step / 4.7 + phase * 2)
            pts.append((int(x), int(y)))
        vd.line(pts, fill=(230, 177, 79, 205), width=7)
        vd.line([(x + 5, y) for x, y in pts], fill=(255, 225, 157, 115), width=3)
    image = Image.alpha_composite(image, veins.filter(ImageFilter.GaussianBlur(18)))
    image = Image.alpha_composite(image, veins)
    draw = ImageDraw.Draw(image)

    gold = (244, 190, 83, 255)
    gold_light = (255, 220, 137, 255)
    gold_shadow = (132, 83, 27, 255)

    # Large centered circular medallion, matching the supplied reference proportions.
    cx, cy, radius = 540, 825, 472
    draw.ellipse((cx-radius, cy-radius, cx+radius, cy+radius),
                 outline=gold_shadow, width=20)
    draw.ellipse((cx-radius+8, cy-radius+8, cx+radius-8, cy+radius-8),
                 outline=gold, width=10)
    draw.ellipse((cx-radius+25, cy-radius+25, cx+radius-25, cy+radius-25),
                 outline=gold_light, width=3)
    draw.ellipse((cx-radius+38, cy-radius+38, cx+radius-38, cy+radius-38),
                 outline=(222, 166, 69, 180), width=2)

    # Symmetrical ornamental crown and lower flourish, kept outside the title area.
    def flourish(y: int, flip: int = 1) -> None:
        top = y
        path = []
        for i in range(121):
            t = i / 120
            x = cx - 180 + 360 * t
            yy = top + flip * (58 * math.sin(math.pi * t) +
                               15 * math.sin(4 * math.pi * t))
            path.append((int(x), int(yy)))
        draw.line(path, fill=gold, width=7)
        draw.line([(x, y + (yy-y)*.82) for x, yy in path],
                  fill=gold_light, width=3)
        for side in (-1, 1):
            for k in range(3):
                x = cx + side * (28 + k * 34)
                yy = y + flip * (22 + k * 7)
                draw.arc((x-34, yy-38, x+34, yy+38), 195, 345,
                         fill=gold_light, width=5)
        draw.polygon([(cx, y-flip*88), (cx-23, y-flip*42),
                      (cx, y-flip*18), (cx+23, y-flip*42)],
                     outline=gold_light, fill=(5, 25, 19, 255))
        draw.line((cx, y-flip*88, cx, y-flip*18), fill=gold, width=5)

    flourish(385, 1)
    flourish(1265, -1)

    # Richer arabesque crown and foot: layered pointed petals and fine scrollwork.
    def arabesque_medallion(y: int, scale: float = 1.0) -> None:
        # Central pointed leaf with nested outlines.
        for inset, color, width_px in ((0, gold_shadow, 12), (7, gold, 7), (13, gold_light, 3)):
            half = int(112 * scale) - inset
            rise = int(104 * scale) - inset
            draw.polygon([(cx, y-rise), (cx+half, y), (cx, y+int(30*scale)),
                          (cx-half, y)], outline=color, width=width_px)
        # Repeated interlaced petal arcs mirror left and right.
        for side in (-1, 1):
            for k in range(4):
                ox = cx + side * int((34 + 38*k) * scale)
                oy = y + int((k % 2) * 8 * scale)
                box = (ox-int(45*scale), oy-int(48*scale),
                       ox+int(45*scale), oy+int(48*scale))
                draw.arc(box, 205 if side < 0 else 335,
                         335 if side < 0 else 475, fill=gold, width=6)
                draw.arc((box[0]+7, box[1]+7, box[2]-7, box[3]-7),
                         205 if side < 0 else 335, 335 if side < 0 else 475,
                         fill=gold_light, width=3)
        # Fine horizontal filigree rails.
        for offset in (-18, 0, 18):
            draw.arc((cx-190*scale, y-55*scale+offset,
                      cx+190*scale, y+55*scale+offset),
                     195, 345, fill=gold, width=4)

    arabesque_medallion(383, 1.0)
    arabesque_medallion(1267, 1.0)

    # Stronger mineral veins with branching hairlines and luminous gold edges.
    for side in (-1, 1):
        for branch in range(8):
            start_x = 18 if side < 0 else width-18
            start_y = 90 + branch*245
            end_x = start_x + side*int(150 + 26*branch)
            end_y = min(height-20, start_y + 310)
            bend = side * (48 + branch*11)
            vein_pts = [(start_x, start_y),
                        (start_x + bend, start_y+85),
                        (end_x-bend//2, start_y+170),
                        (end_x, end_y)]
            draw.line(vein_pts, fill=(218, 159, 64, 245), width=5)
            draw.line([(x+3, y-2) for x,y in vein_pts],
                      fill=(255, 226, 158, 210), width=2)

    # Restrained luminous highlights at the four cardinal points.
    for x, y in ((cx, cy-radius+3), (cx, cy+radius-3),
                 (cx-radius+3, cy), (cx+radius-3, cy)):
        draw.ellipse((x-18, y-18, x+18, y+18), fill=gold_light,
                     outline=gold_shadow, width=4)
        draw.ellipse((x-8, y-8, x+8, y+8), fill=(255, 248, 218, 255))
        draw.line((x-31, y, x+31, y), fill=gold_light, width=3)
        draw.line((x, y-31, x, y+31), fill=gold_light, width=3)

    title_font = ImageFont.truetype(font_path, 142, layout_engine=ImageFont.Layout.RAQM)
    prefix_font = ImageFont.truetype(font_path, 88, layout_engine=ImageFont.Layout.RAQM)
    title = surah_name
    title_box = draw.textbbox((0, 0), title, font=title_font,
                              direction="rtl", language="ar")
    if title_box[2] - title_box[0] > 790:
        title_font = ImageFont.truetype(font_path, 112, layout_engine=ImageFont.Layout.RAQM)
    draw.text((cx, cy-5), title, font=title_font, fill=gold_light,
              anchor="mm", direction="rtl", language="ar")
    draw.text((cx, cy-205), "سورة", font=prefix_font, fill=gold,
              anchor="mm", direction="rtl", language="ar")

    digits = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
    start_text = str(start_ayah).translate(digits)
    end_text = str(end_ayah).translate(digits)
    range_text = (f"الآيات {start_text}" if start_ayah == end_ayah
                  else f"الآيات {start_text} - {end_text}")
    plaque_font = ImageFont.truetype(font_path, 64, layout_engine=ImageFont.Layout.RAQM)
    plaque = (205, 1080, 875, 1215)
    draw.rounded_rectangle(plaque, radius=48, fill=(2, 17, 13, 255),
                           outline=gold_shadow, width=13)
    draw.rounded_rectangle((plaque[0]+9, plaque[1]+9, plaque[2]-9, plaque[3]-9),
                           radius=40, outline=gold_light, width=5)
    draw.text((cx, 1148), range_text, font=plaque_font, fill=(255, 231, 181, 255),
              anchor="mm", direction="rtl", language="ar")
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
            processed_audio = item.get("processed_audio_files", {}).get(str(int(verse["ayah"])))
            audio = (Path(processed_audio) if processed_audio else
                     Path(item["audio_file"]).parent / f"{int(candidate['surah_number']):03d}_{int(verse['ayah']):03d}.mp3")
            if not audio.is_file():
                raise FileNotFoundError(f"Whole-ayah audio file missing: {audio}")
            segment = work / f"segment_{index:02d}.mp4"
            command = [
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                "-stream_loop", "-1", "-i", str(background), "-i", str(audio), "-i", str(frame),
            ]
            if index == 0:
                # The opening title is an overlay on the first ayah segment.
                # It adds no silent lead-in and does not change the audio stream.
                intro = work / "opening_cover.png"
                make_intro_frame(surah_number, int(numbers[0]), int(numbers[-1]),
                                 intro, font_path, SURAH_NAMES[surah_number - 1])
                command.extend(["-loop", "1", "-framerate", "30", "-i", str(intro)])
                filter_complex = (
                    "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30[bg];"
                    "[bg][2:v]overlay=0:0:format=auto[verse];"
                    "[3:v]format=rgba,fade=t=out:st=1.2:d=0.4:alpha=1[intro];"
                    "[verse][intro]overlay=0:0:format=auto[v]"
                )
            else:
                filter_complex = (
                    "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30[bg];"
                    "[bg][2:v]overlay=0:0:format=auto[v]"
                )
            command.extend([
                "-filter_complex", filter_complex,
                "-map", "[v]", "-map", "1:a:0",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                "-pix_fmt", "yuv420p", "-c:a", "copy", "-shortest",
                "-movflags", "+faststart", str(segment)
            ])
            subprocess.run(command, check=True)
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
        "opening_cover": {"included_in_video": True, "duration_seconds": INTRO_DURATION_SECONDS, "fade_seconds": INTRO_FADE_SECONDS, "audio_starts_at_seconds": 0},
        "note": "A short surah-and-ayah opening cover fades over the first ayah while the original recitation starts at t=0; the video remains review-only.",
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
