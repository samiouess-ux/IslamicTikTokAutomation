"""Separate renderer for sourced dua/dhikr; keeps the approved gold visual identity."""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, features

from validate_content_manifest import validate_content_manifest


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def create_overlay(title: str, items: list[dict], destination: Path) -> None:
    if not features.check("raqm"):
        raise SystemExit("Arabic rendering blocked: Pillow libraqm/RAQM is unavailable.")
    try:
        font_path = subprocess.check_output(
            ["fc-match", "-f", "%{file}", "Amiri:style=Bold"], text=True
        ).strip()
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        raise SystemExit("Unable to locate Amiri Bold font.") from exc
    if not font_path or not Path(font_path).is_file():
        raise SystemExit("Required Arabic font is missing.")
    image = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    gold = (231, 190, 103, 255)
    faint = (231, 190, 103, 115)
    outer = [(540,392),(575,410),(785,410),(815,430),(845,475),(815,520),
             (785,540),(575,540),(540,558),(505,540),(295,540),(265,520),
             (235,475),(265,430),(295,410),(505,410)]
    inner = [(540,405),(568,420),(780,420),(802,437),(829,475),(802,513),
             (780,530),(568,530),(540,545),(512,530),(300,530),(278,513),
             (251,475),(278,437),(300,420),(512,420)]
    draw.line(outer + [outer[0]], fill=gold, width=4, joint="curve")
    draw.line(inner + [inner[0]], fill=faint, width=2, joint="curve")
    title_font = ImageFont.truetype(font_path, 58)
    draw.text((540,475), title, font=title_font, fill=gold, anchor="mm",
              direction="rtl", language="ar")
    if not items:
        raise SystemExit("No sourced dua/dhikr text.")
    # Preserve the Arabic source exactly; display one sourced item per screen.
    for item in items:
        if not isinstance(item.get("arabic"), str) or not item["arabic"].strip():
            raise SystemExit("Invalid Arabic source text.")
    text = "\n".join(item["arabic"] for item in items)
    font = ImageFont.truetype(font_path, 64)
    words = text.split()
    lines, current = [], ""
    for word in words:
        candidate = (current + " " + word).strip()
        if draw.textbbox((0,0), candidate, font=font, direction="rtl", language="ar")[2] <= 900:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    if len(lines) > 9:
        raise SystemExit("Dua/dhikr text is too long for the approved layout.")
    line_height = 105
    start_y = 900 - (len(lines)-1)*line_height/2
    for i, line in enumerate(lines):
        draw.text((540,start_y+i*line_height),line,font=font,fill=(255,255,255,255),
                  anchor="mm",direction="rtl",language="ar")
    sources = " | ".join(str(item["source_name"]) for item in items)
    source_font = ImageFont.truetype(font_path, 27)
    draw.text((540,1450),sources,font=source_font,fill=gold,anchor="mm",
              direction="rtl",language="ar")
    image.save(destination)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output", default="output/dua-review.mp4")
    args = parser.parse_args()
    data = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    validate_content_manifest(data)
    if data.get("content_type") not in {"dua", "dhikr"}:
        raise SystemExit("This renderer accepts dua/dhikr manifests only.")
    visual, audio = data["visual"], data["audio"]
    bg = visual.get("approved_background_url") or visual.get("background_candidate", {}).get("direct_video_url")
    if not bg:
        raise SystemExit("An approved background URL is required.")
    if data.get("publishing", {}).get("auto_publish", False):
        raise SystemExit("Auto-publishing is disabled.")
    work = Path("build/dua")
    work.mkdir(parents=True, exist_ok=True)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    overlay = work / "dua_overlay.png"
    create_overlay(data.get("title_ar", "دعاء" if data["content_type"] == "dua" else "ذكر"),
                   data["items"], overlay)
    bg_file = work / "background.mp4"
    subprocess.run(["curl","-fL","--retry","3",bg,"-o",str(bg_file)],check=True)
    kind = audio["kind"]
    inputs = ["-stream_loop","-1","-i",str(bg_file)]
    if kind == "silent":
        duration = float(audio.get("duration_seconds", 0))
        if duration <= 0:
            raise SystemExit("Silent video requires positive audio.duration_seconds.")
        inputs += ["-f","lavfi","-t",str(duration),"-i","anullsrc=r=44100:cl=stereo"]
    else:
        audio_file = Path(audio.get("production_audio_file", ""))
        if not audio_file.is_file():
            raise SystemExit("Approved spoken/ambient audio file is missing.")
        inputs += ["-i",str(audio_file)]
    inputs += ["-i",str(overlay)]
    graph = ("[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
             "crop=1080:1920,setsar=1,fps=30,"
             "drawbox=x=55:y=380:w=970:h=1200:color=black@0.30:t=fill[v0];"
             "[v0][2:v]overlay=0:0[v]")
    run(["ffmpeg","-hide_banner","-y",*inputs,"-filter_complex",graph,
         "-map","[v]","-map","1:a","-shortest","-c:v","libx264","-preset","veryfast",
         "-crf","20","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k",
         "-movflags","+faststart",str(output)])
    print(f"Rendered dua/dhikr review video: {output}")


if __name__ == "__main__":
    main()
