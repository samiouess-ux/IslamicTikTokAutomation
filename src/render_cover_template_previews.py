"""Render four preview-only Quran opening covers; never imported by production."""
from __future__ import annotations

import argparse
import math
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, features

WIDTH, HEIGHT = 1080, 1920
TEMPLATES = ("blue_royal", "emerald_arch", "ivory_classic", "midnight_cinematic")
PALETTES = {
    "blue_royal": ((8, 19, 43), (34, 53, 83), (224, 183, 103), (255, 246, 224)),
    "emerald_arch": ((4, 43, 37), (12, 82, 66), (222, 190, 112), (255, 248, 224)),
    "ivory_classic": ((247, 239, 218), (224, 207, 170), (137, 99, 49), (31, 57, 47)),
    "midnight_cinematic": ((4, 12, 31), (13, 31, 58), (224, 184, 105), (250, 247, 232)),
}


def _font_path() -> str:
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
        t = y / (HEIGHT - 1)
        color = tuple(round(top[i] * (1 - t) + bottom[i] * t) for i in range(3))
        draw.line((0, y, WIDTH, y), fill=color)
    return image.convert("RGBA")


def _star(draw: ImageDraw.ImageDraw, x: int, y: int, radius: int, color: tuple) -> None:
    draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=color)


def _mosque_silhouette(draw: ImageDraw.ImageDraw, color: tuple, y: int) -> None:
    # Restrained distant skyline; the title and verse range remain unobstructed.
    draw.rectangle((0, y+105, WIDTH, HEIGHT), fill=color)
    for cx, radius in ((180, 105), (540, 145), (900, 95)):
        draw.rectangle((cx-radius, y+35, cx+radius, y+115), fill=color)
        draw.pieslice((cx-radius, y- radius//2, cx+radius, y+radius+35),
                      180, 360, fill=color)
        draw.rectangle((cx-5, y-radius//2-35, cx+5, y-radius//2+5), fill=color)
        draw.polygon([(cx, y-radius//2-55), (cx-13, y-radius//2-32),
                      (cx+13, y-radius//2-32)], fill=color)
    for x in (65, 360, 720, 1015):
        draw.rectangle((x-13, y-5, x+13, HEIGHT), fill=color)
        draw.polygon([(x, y-75), (x-18, y-5), (x+18, y-5)], fill=color)


def _arch(draw: ImageDraw.ImageDraw, accent: tuple, inset: int = 105) -> None:
    draw.rounded_rectangle((inset, 170, WIDTH-inset, 1660), radius=390,
                           outline=accent, width=7)
    draw.line((inset, 560, inset, 1580), fill=accent, width=5)
    draw.line((WIDTH-inset, 560, WIDTH-inset, 1580), fill=accent, width=5)
    draw.arc((inset+28, 198, WIDTH-inset-28, 900), 180, 360,
             fill=accent, width=3)


def _background_decor(image: Image.Image, template: str, accent: tuple) -> None:
    draw = ImageDraw.Draw(image, "RGBA")
    if template == "blue_royal":
        _arch(draw, accent)
        # Warm horizon and distant skyline at the foot of the cover.
        _mosque_silhouette(draw, (5, 12, 28, 115), 1650)
        for x, y in ((180, 280), (830, 350), (320, 470), (740, 540)):
            _star(draw, x, y, 3, (*accent, 180))
    elif template == "emerald_arch":
        _arch(draw, accent, 125)
        # Quiet geometric lattice in the outer margins.
        for y in range(250, 1600, 105):
            for x in (72, 1008):
                draw.polygon([(x, y-20), (x+20, y), (x, y+20), (x-20, y)],
                             outline=(*accent, 115), width=2)
        for x in (105, 975):
            draw.rounded_rectangle((x-22, 370, x+22, 520), radius=18,
                                   outline=(*accent, 210), width=4)
            draw.ellipse((x-12, 405, x+12, 485), outline=(*accent, 170), width=2)
    elif template == "ivory_classic":
        for inset, width in ((48, 5), (68, 2), (92, 1)):
            draw.rectangle((inset, inset, WIDTH-inset, HEIGHT-inset),
                           outline=accent, width=width)
        # Delicate corner arabesques, leaving a broad quiet center.
        for x in (115, WIDTH-115):
            for y in (125, HEIGHT-125):
                for radius in (28, 48, 68):
                    draw.arc((x-radius, y-radius, x+radius, y+radius),
                             0, 300, fill=(*accent, 150), width=3)
                draw.ellipse((x-7, y-7, x+7, y+7), fill=accent)
    else:
        # Crescent and fine stars above a distant, low-contrast skyline.
        draw.ellipse((790, 250, 910, 370), fill=(*accent, 245))
        draw.ellipse((830, 220, 950, 340), fill=(8, 19, 42, 255))
        for x, y, r in ((180, 260, 4), (330, 390, 3), (620, 245, 4),
                        (720, 470, 3), (970, 510, 3), (130, 570, 2)):
            _star(draw, x, y, r, (*accent, 190))
        _mosque_silhouette(draw, (1, 6, 19, 150), 1640)


def _draw_title_panel(draw: ImageDraw.ImageDraw, template: str, accent: tuple) -> tuple:
    panel = (105, 650, 975, 990)
    if template == "blue_royal":
        draw.rounded_rectangle(panel, radius=52, fill=(4, 13, 31, 205),
                               outline=(*accent, 255), width=6)
        draw.rounded_rectangle((125, 670, 955, 970), radius=40,
                               outline=(*accent, 125), width=2)
        return (255, 242, 211, 255)
    if template == "emerald_arch":
        draw.rounded_rectangle(panel, radius=155, fill=(2, 35, 30, 190),
                               outline=(*accent, 255), width=5)
        return (255, 248, 224, 255)
    if template == "ivory_classic":
        draw.rectangle(panel, fill=(255, 250, 235, 232),
                       outline=(*accent, 255), width=5)
        draw.rectangle((125, 670, 955, 970), outline=(*accent, 145), width=2)
        return (31, 57, 47, 255)
    draw.rounded_rectangle(panel, radius=24, fill=(1, 7, 20, 195),
                           outline=(*accent, 240), width=4)
    return (255, 247, 224, 255)


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

    top, bottom, accent, _ = PALETTES[template]
    image = _gradient(top, bottom)
    _background_decor(image, template, accent)
    draw = ImageDraw.Draw(image, "RGBA")
    title_color = _draw_title_panel(draw, template, accent)

    font_path = _font_path()
    title_font = None
    for size in (112, 104, 96, 88, 80, 72, 64):
        candidate = ImageFont.truetype(font_path, size, layout_engine=ImageFont.Layout.RAQM)
        bounds = draw.textbbox((540, 805), surah_title, font=candidate,
                               anchor="mm", direction="rtl", language="ar")
        if bounds[2] - bounds[0] <= 760 and bounds[3] - bounds[1] <= 170:
            title_font = candidate
            break
    if title_font is None:
        raise ValueError("Vocalized surah title cannot fit without clipping.")
    draw.text((540, 805), surah_title, font=title_font, fill=title_color,
              anchor="mm", direction="rtl", language="ar")

    digits = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
    first, last = str(start_ayah).translate(digits), str(end_ayah).translate(digits)
    label = f"الآيات {first}" if start_ayah == end_ayah else f"الآيات {first} - {last}"
    range_font = ImageFont.truetype(font_path, 55, layout_engine=ImageFont.Layout.RAQM)
    range_color = (*accent, 255) if template == "ivory_classic" else title_color
    draw.rounded_rectangle((260, 1080, 820, 1190), radius=28,
                           fill=(0, 0, 0, 42) if template != "ivory_classic"
                           else (255, 250, 235, 210),
                           outline=(*accent, 220), width=3)
    draw.text((540, 1135), label, font=range_font, fill=range_color,
              anchor="mm", direction="rtl", language="ar")
    image.save(destination)


def render_all(surah_title: str, start_ayah: int, end_ayah: int,
               output_dir: Path) -> list[Path]:
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
    parser.add_argument("--output-dir", type=Path,
                        default=Path("output/cover_templates_review"))
    args = parser.parse_args()
    outputs = render_all(args.surah_title, args.start_ayah, args.end_ayah,
                         args.output_dir)
    print("PREVIEW ONLY — these covers are not connected to production.")
    for path in outputs:
        print(path)


if __name__ == "__main__":
    main()
