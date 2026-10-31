"""Manifest-driven Quran video renderer with strict Arabic text preservation."""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, features
from hashtag_strategy import build_hashtags
from validate_content_manifest import validate_content_manifest


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


MAX_VIDEO_SECONDS = 65.0


def validate_video_duration(duration: float, maximum: float = MAX_VIDEO_SECONDS) -> None:
    """Reject any render that would exceed the user's strict duration cap."""
    if duration <= 0:
        raise SystemExit("Video duration must be positive.")
    if duration > maximum:
        raise SystemExit(
            f"Video duration {duration:.3f}s exceeds the {maximum:.0f}-second maximum; "
            "select a shorter contiguous verse passage before rendering."
        )


def create_arabic_overlay(title: str, verses: list[dict], destination: Path) -> None:
    """One verse per card; wrap by whole words and shrink only when needed."""
    if len(verses) != 1:
        raise SystemExit("Each screen must contain exactly one verse.")
    if not features.check("raqm"):
        raise SystemExit("Arabic rendering blocked: Pillow libraqm/RAQM is unavailable.")
    # Resolve Amiri Bold through fontconfig because distro font paths can differ.
    try:
        bold_path = subprocess.check_output(
            ["fc-match", "-f", "%{file}", "Amiri:style=Bold"],
            text=True,
        ).strip()
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        raise SystemExit("Unable to locate the Amiri Bold font.") from exc
    if not bold_path or not Path(bold_path).is_file():
        raise SystemExit(f"Required Amiri Bold font is missing: {bold_path!r}")
    image = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    gold = (231, 190, 103, 255)
    soft_gold = (231, 190, 103, 190)
    faint_gold = (231, 190, 103, 105)

    # Restore the approved ornate gold pointed cartouche and rosette details.
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

    def rosette(cx: int, cy: int, radius: int, color) -> None:
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            px = cx + math.cos(rad) * radius * 0.62
            py = cy + math.sin(rad) * radius * 0.62
            draw.ellipse((px-radius*0.38, py-radius*0.38,
                          px+radius*0.38, py+radius*0.38), outline=color, width=2)
        draw.ellipse((cx-3, cy-3, cx+3, cy+3), fill=color)

    rosette(282, 475, 17, gold)
    rosette(798, 475, 17, gold)
    for x in (335, 745):
        draw.polygon([(x,414),(x+7,425),(x,436),(x-7,425)], outline=soft_gold)
        draw.polygon([(x,514),(x+7,525),(x,536),(x-7,525)], outline=soft_gold)

    title_font = ImageFont.truetype(bold_path, 58)
    draw.text((540, 475), title, font=title_font, fill=gold, anchor="mm",
              direction="rtl", language="ar", stroke_width=0)
    verse = verses[0]
    exact_text = verse["arabic"]
    if not isinstance(exact_text, str) or not exact_text.strip():
        raise SystemExit("Invalid/empty Arabic verse text.")
    # Greedy line wrapping retains every original word and its order.
    chosen = None
    for size in (76, 72, 68, 64, 60, 56, 52, 48):
        font = ImageFont.truetype(bold_path, size)
        words = exact_text.split(" ")
        lines, current = [], ""
        for word in words:
            candidate = (current + " " + word).strip()
            if draw.textbbox((0, 0), candidate, font=font, direction="rtl", language="ar")[2] <= 900:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        if len(lines) <= 4:
            chosen = (font, lines)
            break
    if chosen is None:
        raise SystemExit("Verse cannot fit safely; refusing to clip Quran text.")
    font, lines = chosen
    line_height = font.size * 1.75
    first_y = 830 - (len(lines)-1)*line_height/2
    for i, line in enumerate(lines):
        draw.text((540, first_y+i*line_height), line, font=font,
                  fill=(255,255,255,255), anchor="mm", direction="rtl", language="ar")
    # Independent ornamental verse-number medallion.
    cx, cy, radius = 540, 1110, 34
    pts=[]
    for angle in range(0,360,15):
        r=radius if (angle//15)%2==0 else radius-6
        rad=math.radians(angle)
        pts.append((cx+math.cos(rad)*r,cy+math.sin(rad)*r))
    draw.line(pts+[pts[0]], fill=gold, width=3, joint="curve")
    number_font=ImageFont.truetype(bold_path,34)
    number=str(verse["number"]).translate(str.maketrans("0123456789","٠١٢٣٤٥٦٧٨٩"))
    draw.text((cx,cy),number,font=number_font,fill=gold,anchor="mm",direction="rtl",language="ar")
    image.save(destination)

def create_english_overlay(verses: list[dict], destination: Path) -> None:
    """One translation per screen, wrapped with generous line spacing."""
    if len(verses) != 1:
        raise SystemExit("Each screen must contain exactly one translation.")
    font_path="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    font=ImageFont.truetype(font_path,34)
    image=Image.new("RGBA",(1080,1920),(0,0,0,0))
    draw=ImageDraw.Draw(image)
    lines=[]; current=""
    for word in verses[0]["english"].split():
        candidate=(current+" "+word).strip()
        if draw.textbbox((0,0),candidate,font=font)[2] <= 900:
            current=candidate
        else:
            if current: lines.append(current)
            current=word
    if current: lines.append(current)
    if len(lines)>5:
        raise SystemExit("Translation exceeds safe layout.")
    line_h=58
    y=1300-(len(lines)-1)*line_h/2
    for line in lines:
        draw.text((540,y),line,font=font,fill=(255,255,255,255),anchor="mm")
        y+=line_h
    image.save(destination)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output", default="output/review.mp4")
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    validate_content_manifest(data)
    if data.get("content_type", "quran") != "quran":
        raise SystemExit("This renderer currently renders Quran manifests only; dua/dhikr rendering is being added separately.")
    source, audio, visual = data["source"], data["audio"], data["visual"]
    caption = data.get("caption", {})

    # Template selection is manifest-driven. Keep the approved design as the
    # only enabled template until another design is separately reviewed.
    template = visual.get("template", "ornate_gold_classic")
    supported_templates = {"ornate_gold_classic"}
    if template not in supported_templates:
        raise SystemExit(
            f"Unsupported/unapproved visual template: {template}. "
            "Only ornate_gold_classic is currently approved."
        )

    background_url = visual.get("approved_background_url") or visual.get("background_candidate", {}).get("direct_video_url")
    if not background_url:
        raise SystemExit("Manifest must provide an approved background candidate URL.")
    if not audio.get("approved_for_first_test_video", audio.get("approved", False)):
        raise SystemExit("Audio is not marked approved. Refusing to render.")
    exact_recording_reviewed = audio.get("exact_recording_user_reviewed", False) or any(
        item.get("exact_recording_user_reviewed", False)
        for item in audio.get("license_research_candidates", [])
    )
    if not exact_recording_reviewed:
        raise SystemExit("Exact recitation has not been user-reviewed. Refusing to render.")
    background = visual.get("background_candidate", {})
    if not background.get("approved", False):
        raise SystemExit("Background is not marked approved. Refusing to render.")
    if not background.get("user_approved", False):
        raise SystemExit("Background has not been explicitly user-approved. Refusing to render.")
    if data.get("publishing", {}).get("auto_publish", False):
        raise SystemExit("Auto-publishing must remain disabled; renderer is review-only.")

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
    audio_file = Path(audio["production_audio_file"])
    bg_file = work / "background.mp4"
    if not audio_file.is_file():
        raise SystemExit(f"Approved audio file missing: {audio_file}")
    scenes = [{"scene": i, "verses": [n]} for i, n in enumerate(verse_numbers, 1)]
    if [n for scene in scenes for n in scene.get("verses", [])] != verse_numbers:
        raise SystemExit("Scene plan must cover every verse exactly once and in order.")
    scene_overlays = []
    for scene in scenes:
        selected = [v for v in verses if int(v["number"]) in scene["verses"]]
        if not selected or [int(v["number"]) for v in selected] != scene["verses"]:
            raise SystemExit("Scene verse selection is invalid or out of order.")
        arabic_overlay = work / f"arabic_scene_{scene['scene']}.png"
        english_overlay = work / f"english_scene_{scene['scene']}.png"
        create_arabic_overlay(title, selected, arabic_overlay)
        create_english_overlay(selected, english_overlay)
        scene_overlays.append((scene, arabic_overlay, english_overlay))

    verse_durations = {int(k): float(v) for k, v in audio.get("processed_verse_durations_seconds", {}).items()}
    if set(verse_durations) != set(verse_numbers):
        raise SystemExit("Processed verse timing data is incomplete.")
    inter_verse_gap = float(audio.get("inter_verse_silence_seconds", 0.05))
    download(background_url, bg_file)

    # Scene boundaries use the approved processed verse durations.
    scene_boundaries = []
    elapsed = 0.0
    for scene in scenes[:-1]:
        elapsed += sum(verse_durations[n] for n in scene["verses"]) + inter_verse_gap * len(scene["verses"])
        scene_boundaries.append(elapsed)

    duration_result = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=nw=1:nk=1", str(audio_file)
    ], text=True).strip()
    duration = float(duration_result)
    validate_video_duration(duration)

    inputs = ["-stream_loop", "-1", "-i", str(bg_file), "-i", str(audio_file)]
    filters = [
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,setsar=1,fps=30,"
        "drawbox=x=55:y=380:w=970:h=1340:color=black@0.30:t=fill[vbase]"
    ]
    current = "vbase"
    input_index = 2
    for index, (scene, arabic_overlay, english_overlay) in enumerate(scene_overlays):
        inputs += ["-i", str(arabic_overlay), "-i", str(english_overlay)]
        start = 0.0 if index == 0 else scene_boundaries[index - 1]
        end = duration if index == len(scene_overlays) - 1 else scene_boundaries[index]
        filters.append(
            f"[{current}][{input_index}:v]overlay=0:0:enable='between(t,{start:.6f},{end:.6f})'[v{index}a]"
        )
        filters.append(
            f"[v{index}a][{input_index + 1}:v]overlay=0:0:enable='between(t,{start:.6f},{end:.6f})'[v{index}]"
        )
        current = f"v{index}"
        input_index += 2
    draw = ";".join(filters)
    run([
        "ffmpeg", "-hide_banner", "-y", *inputs, "-filter_complex", draw,
        "-map", f"[{current}]", "-map", "1:a", "-t", str(duration),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart", str(output)
    ])

    caption_path = output.with_suffix(".caption.json")
    hashtag_sets = build_hashtags(str(data.get("id", "")), caption)
    caption_path.write_text(json.dumps({
        "status": "review_required",
        "surah": source["surah_name_ar"],
        "verses": verse_numbers,
        "arabic_caption": caption.get("arabic", ""),
        "english_caption": caption.get("english", ""),
        "hashtags_ar": hashtag_sets["ar"],
        "hashtags_en": hashtag_sets["en"],
        "hashtags_fr": hashtag_sets["fr"],
        "hashtags_tr": hashtag_sets["tr"],
        "hashtags_id": hashtag_sets["id"],
        "reciter_public_attribution": False,
        "publishing": "disabled"
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Rendered review video: {output} ({duration:.2f}s)")
    print(f"Caption for review: {caption_path}")


if __name__ == "__main__":
    main()
