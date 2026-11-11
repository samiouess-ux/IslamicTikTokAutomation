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


MAX_BACKGROUND_DOWNLOAD_BYTES = 250 * 1024 * 1024


def download(url: str, destination: Path) -> None:
    """Download a bounded background file and remove partial output on failure."""
    request = urllib.request.Request(url, headers={"User-Agent": "IslamicTikTokAutomation/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            declared_size = response.headers.get("Content-Length")
            if declared_size is not None and int(declared_size) > MAX_BACKGROUND_DOWNLOAD_BYTES:
                raise SystemExit("Background download exceeds the 250 MiB safety limit.")
            total = 0
            with destination.open("wb") as out:
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > MAX_BACKGROUND_DOWNLOAD_BYTES:
                        raise SystemExit("Background download exceeds the 250 MiB safety limit.")
                    out.write(chunk)
            if total == 0:
                raise SystemExit("Background download returned an empty file.")
    except BaseException:
        destination.unlink(missing_ok=True)
        raise


def ffmpeg_text(value: str) -> str:
    return (value.replace("\\", "\\\\").replace(":", "\\:")
            .replace("'", "\\'").replace("%", "\\%")
            .replace(",", "\\,").replace("[", "\\[").replace("]", "\\]"))


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


MAX_VIDEO_SECONDS = 40.0


def validate_video_duration(duration: float, maximum: float = MAX_VIDEO_SECONDS) -> None:
    """Reject non-finite, non-positive, or over-limit render durations."""
    if not math.isfinite(duration):
        raise SystemExit("Video duration must be a finite number.")
    if duration <= 0:
        raise SystemExit("Video duration must be positive.")
    if duration > maximum:
        raise SystemExit(
            f"Video duration {duration:.3f}s exceeds the {maximum:.0f}-second maximum; "
            "select a shorter contiguous verse passage before rendering."
        )


def validate_quran_audio_approval(audio: dict) -> None:
    """Allow approved audio or an explicitly rights-cleared review-only preview."""
    preview_only = audio.get("preview_only") is True
    approved = audio.get("approved_for_first_test_video", audio.get("approved", False)) is True
    if not approved and not preview_only:
        raise SystemExit("Audio is not marked approved. Refusing to render.")
    if preview_only and approved:
        raise SystemExit("A preview-only recording cannot be marked production-approved.")
    exact_recording_reviewed = audio.get("exact_recording_user_reviewed", False) or any(
        item.get("exact_recording_user_reviewed", False)
        for item in audio.get("license_research_candidates", [])
        if isinstance(item, dict)
    )
    if not exact_recording_reviewed and not preview_only:
        raise SystemExit("Exact recitation has not been user-reviewed. Refusing to render.")
    rights_verified = audio.get("rights_verified") or any(
        item.get("status", "").startswith("approved_")
        for item in audio.get("license_research_candidates", [])
        if isinstance(item, dict)
    )
    if not rights_verified:
        raise SystemExit("Reuse permission for the exact Quran recording is not documented.")


def create_arabic_overlay(title: str, verses: list[dict], destination: Path,
                           template: str = "ornate_gold_classic") -> None:
    """Render one exact Quran verse in one of four genuinely distinct layouts."""
    templates = {"ornate_gold_classic", "nature_clean", "minimal_mushaf", "cinematic_landscape"}
    if template not in templates:
        raise SystemExit(f"Unsupported visual template: {template}")
    if len(verses) != 1:
        raise SystemExit("Each screen must contain exactly one verse.")
    if not features.check("raqm"):
        raise SystemExit("Arabic rendering blocked: Pillow libraqm/RAQM is unavailable.")
    try:
        bold_path = subprocess.check_output(
            ["fc-match", "-f", "%{file}", "Amiri:style=Bold"], text=True
        ).strip()
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        raise SystemExit("Unable to locate the Amiri Bold font.") from exc
    if not bold_path or not Path(bold_path).is_file():
        raise SystemExit(f"Required Amiri Bold font is missing: {bold_path!r}")
    image = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    palettes = {
        "ornate_gold_classic": ((231,190,103,255),(255,255,255,255)),
        "nature_clean": ((205,238,211,255),(255,255,255,255)),
        "minimal_mushaf": ((238,226,195,255),(255,255,245,255)),
        "cinematic_landscape": ((190,220,255,255),(255,255,255,255)),
    }
    accent, text_color = palettes[template]
    title_font = ImageFont.truetype(bold_path, 58 if template != "minimal_mushaf" else 52)
    if template == "ornate_gold_classic":
        outer = [(540,392),(575,410),(785,410),(815,430),(845,475),(815,520),
                 (785,540),(575,540),(540,558),(505,540),(295,540),(265,520),
                 (235,475),(265,430),(295,410),(505,410)]
        draw.line(outer+[outer[0]], fill=accent, width=4, joint="curve")
        for cx in (282,798):
            for angle in range(0,360,45):
                rad=math.radians(angle)
                px=cx+math.cos(rad)*10; py=475+math.sin(rad)*10
                draw.ellipse((px-5,py-5,px+5,py+5),outline=accent,width=2)
        title_y=475
    elif template == "nature_clean":
        draw.rounded_rectangle((95,385,985,565),radius=48,outline=accent,width=5)
        draw.line((170,590,910,590),fill=accent,width=3)
        title_y=475
    elif template == "minimal_mushaf":
        draw.line((140,420,940,420),fill=accent,width=3)
        draw.line((140,535,940,535),fill=accent,width=3)
        draw.ellipse((520,463,560,503),outline=accent,width=2)
        title_y=475
    else:
        draw.rounded_rectangle((65,365,1015,580),radius=12,outline=accent,width=3)
        draw.line((120,600,960,600),fill=accent,width=2)
        title_y=475
    draw.text((540,title_y),title,font=title_font,fill=accent,anchor="mm",
              direction="rtl",language="ar")
    verse=verses[0]
    exact_text=verse.get("arabic")
    if not isinstance(exact_text,str) or not exact_text.strip():
        raise SystemExit("Invalid/empty Arabic verse text.")
    chosen=None
    for size in (76,72,68,64,60,56,52,48):
        font=ImageFont.truetype(bold_path,size)
        words=exact_text.split(" "); lines=[]; current=""
        for word in words:
            candidate=(current+" "+word).strip()
            if draw.textbbox((0,0),candidate,font=font,direction="rtl",language="ar")[2] <= 900:
                current=candidate
            else:
                if current: lines.append(current)
                current=word
        if current: lines.append(current)
        if len(lines)<=4:
            chosen=(font,lines); break
    if chosen is None:
        raise SystemExit("Verse cannot fit safely; refusing to clip Quran text.")
    font,lines=chosen
    line_height=font.size*1.75
    first_y=850-(len(lines)-1)*line_height/2
    for i,line in enumerate(lines):
        draw.text((540,first_y+i*line_height),line,font=font,fill=text_color,
                  anchor="mm",direction="rtl",language="ar")
    number=str(verse["number"]).translate(str.maketrans("0123456789","٠١٢٣٤٥٦٧٨٩"))
    number_font=ImageFont.truetype(bold_path,34)
    if template == "ornate_gold_classic":
        cx,cy,radius=540,1110,34
        pts=[]
        for angle in range(0,360,15):
            r=radius if (angle//15)%2==0 else radius-6
            rad=math.radians(angle); pts.append((cx+math.cos(rad)*r,cy+math.sin(rad)*r))
        draw.line(pts+[pts[0]],fill=accent,width=3,joint="curve")
        draw.text((cx,cy),number,font=number_font,fill=accent,anchor="mm",direction="rtl",language="ar")
    elif template == "nature_clean":
        draw.rounded_rectangle((485,1080,595,1140),radius=28,outline=accent,width=3)
        draw.text((540,1110),number,font=number_font,fill=accent,anchor="mm",direction="rtl",language="ar")
    elif template == "minimal_mushaf":
        draw.text((540,1110),f"۞ {number} ۞",font=number_font,fill=accent,anchor="mm",direction="rtl",language="ar")
    else:
        draw.line((390,1110,690,1110),fill=accent,width=2)
        draw.text((540,1160),number,font=number_font,fill=accent,anchor="mm",direction="rtl",language="ar")
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



def probe_media_duration(path: Path) -> float:
    result = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=nw=1:nk=1", str(path)
    ], text=True).strip()
    duration = float(result)
    if not math.isfinite(duration) or duration <= 0:
        raise SystemExit(f"Invalid media duration for {path}: {duration}")
    return duration


def validate_rendered_video(path: Path, expected_duration: float) -> None:
    """Verify generated reel output is a real 1080x1920 video of sufficient length."""
    if not path.is_file() or path.stat().st_size == 0:
        raise SystemExit(f"Generated background video is missing or empty: {path}")
    raw = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_streams", "-show_format",
        "-of", "json", str(path)
    ], text=True)
    try:
        info = json.loads(raw)
        video = next(s for s in info.get("streams", []) if s.get("codec_type") == "video")
        width, height = int(video["width"]), int(video["height"])
        actual_duration = float(info["format"]["duration"])
    except (ValueError, TypeError, KeyError, StopIteration, json.JSONDecodeError) as exc:
        raise SystemExit(f"Generated background is not a readable video: {path}") from exc
    if (width, height) != (1080, 1920):
        raise SystemExit(f"Generated background must be 1080x1920; got {width}x{height}: {path}")
    if not math.isfinite(actual_duration) or actual_duration + 0.10 < expected_duration:
        raise SystemExit(
            f"Generated background is too short or has invalid duration "
            f"({actual_duration:.3f}s for {expected_duration:.3f}s): {path}"
        )


def probe_background_media(path: Path) -> float:
    """Fail closed unless a downloaded background is a valid 9:16 video."""
    if not path.is_file() or path.stat().st_size == 0:
        raise SystemExit(f"Downloaded background is missing or empty: {path}")
    raw = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_streams", "-show_format",
        "-of", "json", str(path)
    ], text=True)
    try:
        info = json.loads(raw)
        video = next(
            stream for stream in info.get("streams", [])
            if stream.get("codec_type") == "video"
        )
        width, height = int(video["width"]), int(video["height"])
        duration = float(info["format"]["duration"])
    except (ValueError, TypeError, KeyError, StopIteration, json.JSONDecodeError) as exc:
        raise SystemExit(f"Downloaded background is not a readable video: {path}") from exc
    if width <= 0 or height <= 0 or not math.isclose(
        width / height, 9 / 16, rel_tol=0.02
    ):
        raise SystemExit(
            f"Background must be portrait 9:16; got {width}x{height}: {path}"
        )
    if not math.isfinite(duration) or duration <= 0:
        raise SystemExit(f"Invalid background duration for {path}: {duration}")
    return duration


def build_background_reel(
    candidates: list[dict], duration: float, work: Path, destination: Path
) -> None:
    """Join approved clips in order, trimming the final clip to the audio length."""
    if not math.isfinite(duration) or duration <= 0:
        raise SystemExit("Background reel duration must be a finite positive number.")
    if not candidates:
        raise SystemExit("No approved backgrounds are available for this render.")
    raw_files: dict[str, Path] = {}
    clip_durations: dict[str, float] = {}
    normalized_files: list[Path] = []
    remaining = duration
    sequence_index = 0
    cycles = 0

    while remaining > 0.02:
        cycles += 1
        if cycles > 20:
            raise SystemExit("Background clips could not cover the full audio duration.")
        progress_before_cycle = remaining
        for candidate in candidates:
            candidate_id = candidate["id"]
            if candidate_id not in raw_files:
                raw_path = work / f"background_source_{len(raw_files)}.mp4"
                download(candidate["direct_video_url"], raw_path)
                raw_files[candidate_id] = raw_path
                clip_durations[candidate_id] = probe_background_media(raw_path)
            take = min(clip_durations[candidate_id], remaining)
            if take <= 0.02:
                continue
            normalized = work / f"background_scene_{sequence_index:03d}.mp4"
            run([
                "ffmpeg", "-hide_banner", "-y", "-i", str(raw_files[candidate_id]),
                "-t", f"{take:.6f}",
                "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,"
                       "crop=1080:1920,setsar=1,fps=30,format=yuv420p",
                "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                "-pix_fmt", "yuv420p", "-r", "30", str(normalized)
            ])
            validate_rendered_video(normalized, take)
            normalized_files.append(normalized)
            remaining -= take
            sequence_index += 1
            if remaining <= 0.02:
                break
        if progress_before_cycle - remaining <= 0.02:
            raise SystemExit("Approved background clips have no usable duration.")

    concat_list = work / "background_concat.txt"
    concat_list.write_text(
        "".join("file '" + path.resolve().as_posix() + "'\n" for path in normalized_files),
        encoding="utf-8",
    )
    run([
        "ffmpeg", "-hide_banner", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_list), "-an", "-c", "copy", "-movflags", "+faststart",
        str(destination)
    ])
    validate_rendered_video(destination, duration)


def prepare_manifest_background(
    data: dict,
    background_rotation: bool,
    rotation_key: str,
    recent_background_ids: list[str],
) -> list[dict] | None:
    """Apply an eligible rotated background before validating the manifest."""
    background_sequence = None
    if background_rotation:
        visual = data.get("visual")
        if not isinstance(visual, dict):
            raise SystemExit("Manifest visual must be an object before background rotation.")
        from background_rotation import order_backgrounds
        background_sequence = order_backgrounds(
            Path("data/background_candidates.json"),
            rotation_key,
            recent_background_ids,
        )
        selected_background = dict(background_sequence[0])
        background_sequence = [dict(item) for item in background_sequence]
        selected_background["source_url"] = selected_background["source_page_url"]
        visual["background_candidate"] = selected_background
        visual.pop("approved_background_url", None)
        print(f"Selected approved background: {selected_background['id']}")
    validate_content_manifest(data)
    return background_sequence




def calculate_scene_boundaries(
    scenes: list[dict],
    verse_durations: dict[int, float],
    inter_verse_gap: float,
    audio_duration: float,
) -> list[float]:
    """Calculate strictly increasing verse-screen boundaries inside the audio."""
    if not math.isfinite(audio_duration) or audio_duration <= 0:
        raise SystemExit("Scene timing requires a finite positive audio duration.")
    if not math.isfinite(inter_verse_gap) or inter_verse_gap < 0:
        raise SystemExit("Inter-verse gap must be finite and non-negative.")
    if any(not math.isfinite(value) or value <= 0 for value in verse_durations.values()):
        raise SystemExit("Every processed verse duration must be finite and positive.")
    boundaries = []
    elapsed = 0.0
    for scene in scenes[:-1]:
        numbers = scene.get("verses")
        if not isinstance(numbers, list) or not numbers:
            raise SystemExit("Scene timing requires a non-empty verse list.")
        try:
            elapsed += sum(verse_durations[number] for number in numbers)
        except KeyError as exc:
            raise SystemExit(f"Missing processed duration for verse {exc.args[0]}.") from exc
        elapsed += inter_verse_gap * len(numbers)
        if not math.isfinite(elapsed) or elapsed <= (boundaries[-1] if boundaries else 0.0):
            raise SystemExit("Scene timing boundaries must be finite and strictly increasing.")
        if elapsed >= audio_duration:
            raise SystemExit("A verse scene boundary falls at or beyond the end of the audio.")
        boundaries.append(elapsed)
    planned_duration = sum(
        verse_durations[number]
        for scene in scenes
        for number in scene.get("verses", [])
    ) + inter_verse_gap * sum(
        len(scene.get("verses", [])) for scene in scenes[:-1]
    )
    if abs(planned_duration - audio_duration) > 0.50:
        raise SystemExit(
            f"Processed verse timings differ from the audio duration "
            f"({planned_duration:.3f}s planned vs {audio_duration:.3f}s actual)."
        )
    return boundaries



def validate_final_review_video(path: Path, expected_duration: float) -> None:
    """Fail closed unless the composed review MP4 has valid video and audio."""
    if not path.is_file() or path.stat().st_size == 0:
        raise SystemExit(f"Final review video is missing or empty: {path}")
    if not math.isfinite(expected_duration) or expected_duration <= 0:
        raise SystemExit("Expected final video duration must be finite and positive.")
    raw = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_streams", "-show_format",
        "-of", "json", str(path)
    ], text=True)
    try:
        info = json.loads(raw)
        streams = info.get("streams", [])
        video = next(s for s in streams if s.get("codec_type") == "video")
        audio = next(s for s in streams if s.get("codec_type") == "audio")
        width, height = int(video["width"]), int(video["height"])
        duration = float(info["format"]["duration"])
        video_duration = float(video["duration"])
        audio_duration = float(audio["duration"])
        frame_rate = video.get("avg_frame_rate") or video.get("r_frame_rate")
        numerator, denominator = (int(part) for part in frame_rate.split("/", 1))
        fps = numerator / denominator
    except (ValueError, TypeError, KeyError, StopIteration, ZeroDivisionError,
            json.JSONDecodeError, AttributeError) as exc:
        raise SystemExit(f"Final review file is not a readable audio/video MP4: {path}") from exc
    if (width, height) != (1080, 1920):
        raise SystemExit(f"Final review video must be 1080x1920; got {width}x{height}: {path}")
    if not math.isfinite(fps) or not math.isclose(fps, 30.0, abs_tol=0.01):
        raise SystemExit(f"Final review video must be 30 fps; got {frame_rate}: {path}")
    if (not math.isfinite(duration) or not math.isfinite(video_duration)
            or not math.isfinite(audio_duration)
            or video_duration < expected_duration - 0.25
            or audio_duration < expected_duration - 0.25):
        raise SystemExit(
            f"Final review streams do not cover the approved audio "
            f"(container={duration:.3f}s, video={video_duration:.3f}s, "
            f"audio={audio_duration:.3f}s; expected={expected_duration:.3f}s): {path}"
        )
    if duration > MAX_VIDEO_SECONDS or duration > expected_duration + 0.50:
        raise SystemExit(f"Final review video duration is outside the allowed range ({duration:.3f}s for {expected_duration:.3f}s): {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output", default="output/review.mp4")
    parser.add_argument("--background-rotation", action="store_true", help="Select from the approved background catalog.")
    parser.add_argument("--background-rotation-key", default="manual-review")
    parser.add_argument("--recent-background-id", action="append", default=[])
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    background_sequence = prepare_manifest_background(
        data,
        args.background_rotation,
        args.background_rotation_key,
        args.recent_background_id,
    )
    if data.get("content_type", "quran") != "quran":
        raise SystemExit("This renderer currently renders Quran manifests only; dua/dhikr rendering is being added separately.")
    source, audio, visual = data["source"], data["audio"], data["visual"]
    caption = data.get("caption", {})

    # Template selection is manifest-driven. Keep the approved design as the
    # only enabled template until another design is separately reviewed.
    template = visual.get("template", "ornate_gold_classic")
    supported_templates = {"ornate_gold_classic", "nature_clean", "minimal_mushaf", "cinematic_landscape"}
    if template not in supported_templates:
        raise SystemExit(
            f"Unsupported/unapproved visual template: {template}. "
            "Only ornate_gold_classic is currently approved."
        )

    background_url = visual.get("approved_background_url") or visual.get("background_candidate", {}).get("direct_video_url")
    if not background_url:
        raise SystemExit("Manifest must provide an approved background candidate URL.")
    validate_quran_audio_approval(audio)
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
        create_arabic_overlay(title, selected, arabic_overlay, template)
        create_english_overlay(selected, english_overlay)
        scene_overlays.append((scene, arabic_overlay, english_overlay))

    verse_durations = {int(k): float(v) for k, v in audio.get("processed_verse_durations_seconds", {}).items()}
    if set(verse_durations) != set(verse_numbers):
        raise SystemExit("Processed verse timing data is incomplete.")
    inter_verse_gap = float(audio.get("inter_verse_silence_seconds", 0.05))
    # The background reel is built after the exact audio duration is known.

    duration_result = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=nw=1:nk=1", str(audio_file)
    ], text=True).strip()
    duration = float(duration_result)
    validate_video_duration(duration)

    # Scene boundaries use the approved processed verse durations.
    scene_boundaries = calculate_scene_boundaries(
        scenes, verse_durations, inter_verse_gap, duration
    )
    build_background_reel(
        background_sequence or [background], duration, work, bg_file
    )

    inputs = ["-i", str(bg_file), "-i", str(audio_file)]
    filters = [
        "[0:v]tpad=stop_mode=clone:stop_duration=1,scale=1080:1920:force_original_aspect_ratio=increase,"
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
    validate_final_review_video(output, duration)

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
