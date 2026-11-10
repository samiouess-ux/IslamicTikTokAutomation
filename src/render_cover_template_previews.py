"""Create four independent, preview-only Quran opening-cover designs.

This module is intentionally not imported by the production video pipeline.
Arabic surah names must be supplied already vocalized from an approved source.
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps, features

WIDTH, HEIGHT = 1080, 1920
TEMPLATES = ("gold_ornate", "emerald_arch", "ivory_mushaf", "midnight_cinematic")
PALETTES = {
    "gold_ornate": ((17, 23, 30), (48, 35, 22), (235, 193, 112), (255, 244, 220)),
    "emerald_arch": ((5, 43, 39), (10, 79, 65), (208, 190, 125), (255, 250, 230)),
    "ivory_mushaf": ((238, 226, 198), (212, 192, 153), (117, 86, 49), (48, 43, 35)),
    "midnight_cinematic": ((9, 18, 40), (30, 42, 73), (147, 190, 225), (247, 249, 255)),
}


def _font_path() -> str:
    import subprocess
    path = subprocess.check_output(
        ["fc-match", "-f", "%{file}", "Amiri:style=Bold"], text=True
    ).strip()
    if not path or not Path(path).is_file():
        raise RuntimeError("Amiri Bold font is required for Arabic cover previews.")
    return path


def _gradient(top: tuple, bottom: tuple) -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(image)
    for y in range(HEIGHT):
        ratio = y / (HEIGHT - 1)
        color = tuple(round(top[i] * (1-ratio) + bottom[i] * ratio) for i in range(3))
        draw.line((0, y, WIDTH, y), fill=color)
    return image.convert("RGBA")


def _ornament(draw: ImageDraw.ImageDraw, accent: tuple, template: str) -> None:
    if template == "gold_ornate":
        for inset, width in ((42, 4), (58, 1)):
            draw.rounded_rectangle((inset, inset, WIDTH-inset, HEIGHT-inset),
                                   radius=34, outline=accent, width=width)
        for x in (105, WIDTH-105):
            for y in (150, HEIGHT-150):
                draw.polygon([(x,y-28),(x+8,y-8),(x+28,y),(x+8,y+8),
                              (x,y+28),(x-8,y+8),(x-28,y),(x-8,y-8)],
                             outline=accent)
    elif template == "emerald_arch":
        draw.arc((125, 190, 955, 1100), 180, 360, fill=accent, width=8)
        draw.line((125, 645, 125, 1390), fill=accent, width=6)
        draw.line((955, 645, 955, 1390), fill=accent, width=6)
        draw.ellipse((495, 205, 585, 295), outline=accent, width=4)
    elif template == "ivory_mushaf":
        for inset, width in ((74, 5), (91, 2)):
            draw.rectangle((inset, inset, WIDTH-inset, HEIGHT-inset),
                           outline=accent, width=width)
        for y in (350, 1480):
            draw.line((230, y, 850, y), fill=accent, width=3)
            draw.ellipse((528, y-8, 552, y+8), fill=accent)
    else:
        draw.rounded_rectangle((68, 220, 1012, 1690), radius=24,
                               outline=accent, width=3)
        for x in range(160, 1000, 110):
            draw.line((x, 250, x+160, 250), fill=(*accent[:3], 90), width=1)


def render_cover(surah_title: str, start_ayah: int, end_ayah: int,
                 template: str, destination: Path) -> None:
    """Render one opening cover. Title must include correct Arabic diacritics."""
    if not features.check("raqm"):
        raise RuntimeError("Pillow RAQM support is required for safe Arabic shaping.")
    if template not in TEMPLATES:
        raise ValueError(f"Unknown cover template: {template}")
    if not isinstance(surah_title, str) or not surah_title.strip():
        raise ValueError("A fully vocalized Arabic surah title is required.")
    if start_ayah < 1 or end_ayah < start_ayah:
        raise ValueError("Ayah range must be positive and ordered.")

    top, bottom, accent, text_color = PALETTES[template]
    image = _gradient(top, bottom)
    draw = ImageDraw.Draw(image, "RGBA")
    _ornament(draw, accent, template)

    # A distinct title treatment for each design, all within a safe text area.
    if template == "gold_ornate":
        draw.rounded_rectangle((110, 650, 970, 930), radius=48,
                               fill=(0, 0, 0, 82), outline=(*accent, 245), width=5)
        title_y, title_color = 790, accent
    elif template == "emerald_arch":
        draw.rounded_rectangle((145, 660, 935, 930), radius=135,
                               fill=(0, 0, 0, 55), outline=(*accent, 235), width=4)
        title_y, title_color = 795, text_color
    elif template == "ivory_mushaf":
        draw.rectangle((125, 650, 955, 930), fill=(255, 250, 235, 190),
                       outline=(*accent, 255), width=4)
        title_y, title_color = 790, accent
    else:
        draw.rounded_rectangle((105, 650, 975, 930), radius=16,
                               fill=(3, 8, 20, 125), outline=(*accent, 225), width=3)
        title_y, title_color = 790, text_color

    title_font = None
    for size in (112, 104, 96, 88, 80, 72, 64):
        candidate = ImageFont.truetype(_font_path(), size, layout_engine=ImageFont.Layout.RAQM)
        bounds = draw.textbbox((540, title_y), surah_title, font=candidate,
                               anchor="mm", direction="rtl", language="ar")
        if bounds[2]-bounds[0] <= 760 and bounds[3]-bounds[1] <= 160:
            title_font = candidate
            break
    if title_font is None:
        raise ValueError("Vocalized surah title cannot fit without clipping.")
    draw.text((540, title_y), surah_title, font=title_font, fill=title_color,
              anchor="mm", direction="rtl", language="ar")

    digits = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
    a, b = str(start_ayah).translate(digits), str(end_ayah).translate(digits)
    range_label = f"الآيات {a}" if start_ayah == end_ayah else f"الآيات {a} - {b}"
    range_font = ImageFont.truetype(_font_path(), 54, layout_engine=ImageFont.Layout.RAQM)
    draw.text((540, 1085), range_label, font=range_font, fill=text_color,
              anchor="mm", direction="rtl", language="ar")
    draw.line((320, 1190, 760, 1190), fill=(*accent, 220), width=3)
    image.save(destination)


def render_all(surah_title: str, start_ayah: int, end_ayah: int, output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = []
    for template in TEMPLATES:
        path = output_dir / f"{template}.png"
        render_cover(surah_title, start_ayah, end_ayah, template, path)
        outputs.append(path)
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--surah-title", required=True,
                        help="Fully vocalized Arabic title from an approved source")
    parser.add_argument("--start-ayah", type=int, required=True)
    parser.add_argument("--end-ayah", type=int, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("output/cover_templates_review"))
    args = parser.parse_args()
    outputs = render_all(args.surah_title, args.start_ayah, args.end_ayah, args.output_dir)
    print("PREVIEW ONLY — these covers are not connected to production.")
    for path in outputs:
        print(path)


if __name__ == "__main__":
    main()
