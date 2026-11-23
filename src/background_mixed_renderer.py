"""Render mixed approved photo/video background reels for Quran scenes.

This module keeps media-specific preparation separate, then crossfades the
normalized scene clips into one 9:16 reel. It does not publish or send media.
"""
from __future__ import annotations

import hashlib
import math
import subprocess
import urllib.request
from pathlib import Path

from PIL import Image


def select_scene_backgrounds(
    assets: list[dict], scene_count: int, rotation_key: str,
    recent_ids: list[str] | tuple[str, ...] = (),
) -> list[dict]:
    """Deterministically rotate approved assets, preferring media-type variety."""
    if scene_count < 1:
        raise ValueError("At least one scene is required.")
    if not rotation_key.strip():
        raise ValueError("A non-empty background rotation key is required.")
    if not assets:
        raise ValueError("No approved mixed background assets are available.")
    ids = [item.get("asset_id") for item in assets]
    if any(not value for value in ids) or len(ids) != len(set(ids)):
        raise ValueError("Mixed background asset IDs must be present and unique.")

    recent = set(recent_ids)
    unused = [item for item in assets if item["asset_id"] not in recent]
    if not unused:
        unused = list(assets)
    selected: list[dict] = []
    pool = list(unused)
    previous_type = None
    for index in range(scene_count):
        available = [item for item in pool if item["media_type"] != previous_type]
        if not available:
            available = pool
        if not available:
            pool = list(assets)
            available = [item for item in pool if item["media_type"] != previous_type] or pool

        def score(item: dict) -> str:
            return hashlib.sha256(
                f"{rotation_key}:{index}:{item['asset_id']}".encode("utf-8")
            ).hexdigest()

        chosen = min(available, key=score)
        selected.append(chosen)
        previous_type = chosen["media_type"]
        pool = [item for item in pool if item["asset_id"] != chosen["asset_id"]]
    return selected


def _run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def _probe(path: Path) -> tuple[float, int, int]:
    raw = subprocess.check_output([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height:format=duration",
        "-of", "default=noprint_wrappers=1", str(path)
    ], text=True)
    values = {}
    for line in raw.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            values[key] = value
    duration = float(values["duration"])
    width, height = int(values["width"]), int(values["height"])
    if not math.isfinite(duration) or duration <= 0 or width <= 0 or height <= 0:
        raise ValueError(f"Invalid background media metadata: {path}")
    return duration, width, height


def _download(url: str, destination: Path) -> None:
    request = urllib.request.Request(
        url, headers={"User-Agent": "IslamicTikTokAutomation/1.0"}
    )
    with urllib.request.urlopen(request, timeout=90) as response, destination.open("wb") as out:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)
    if destination.stat().st_size < 50_000:
        raise ValueError(f"Downloaded background is unexpectedly small: {destination}")


def build_mixed_background_reel(
    assets: list[dict], scenes: list[dict], duration: float, work: Path,
    destination: Path, rotation_key: str, recent_ids: list[str] | tuple[str, ...] = (),
) -> list[str]:
    """Prepare each chosen photo/video scene independently and crossfade them."""
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError("Mixed background duration must be finite and positive.")
    if not scenes:
        raise ValueError("No timed scenes were supplied for mixed backgrounds.")
    if not rotation_key.strip():
        raise ValueError("A non-empty mixed background rotation key is required.")

    chosen = select_scene_backgrounds(assets, len(scenes), rotation_key, recent_ids)
    scene_durations = [float(scene["duration"]) for scene in scenes]
    if any(not math.isfinite(value) or value <= 0 for value in scene_durations):
        raise ValueError("Every mixed background scene must have a finite positive duration.")
    scene_durations[-1] += duration - sum(scene_durations)
    if scene_durations[-1] <= 0:
        raise ValueError("Timed background scenes exceed the audio duration.")

    work.mkdir(parents=True, exist_ok=True)
    destination.parent.mkdir(parents=True, exist_ok=True)
    transition = min(0.6, min(scene_durations) * 0.20) if len(chosen) > 1 else 0.0
    segments: list[Path] = []

    for index, (asset, scene_duration) in enumerate(zip(chosen, scene_durations)):
        clip_duration = scene_duration + (transition if index < len(chosen) - 1 else 0.0)
        segment = work / f"mixed_background_scene_{index}.mp4"
        if asset["media_type"] == "photo":
            source = Path(asset["asset_path"])
            if not source.is_file() or source.stat().st_size < 50_000:
                raise ValueError(f"Approved photo is missing or too small: {asset['asset_id']}")
            with Image.open(source) as image:
                image.verify()
            with Image.open(source) as image:
                if image.width < 720 or image.height < 720:
                    raise ValueError(f"Approved photo dimensions are too small: {asset['asset_id']}")
            _run([
                "ffmpeg", "-hide_banner", "-y", "-loop", "1", "-framerate", "30",
                "-t", f"{clip_duration:.6f}", "-i", str(source),
                "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,"
                       "crop=1080:1920,setsar=1,zoompan="
                       "z='min(1+0.00012*on,1.035)':"
                       "x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2':"
                       "d=1:s=1080x1920:fps=30,format=yuv420p",
                "-an", "-t", f"{clip_duration:.6f}", "-c:v", "libx264",
                "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                "-r", "30", str(segment)
            ])
        elif asset["media_type"] == "video":
            url = asset.get("asset_url")
            if not isinstance(url, str) or not url.startswith("https://"):
                raise ValueError(f"Approved video has no verified HTTPS source: {asset['asset_id']}")
            raw = work / f"mixed_background_source_{index}.mp4"
            _download(url, raw)
            _, width, height = _probe(raw)
            if height <= width or width / height > 0.70:
                raise ValueError(f"Video is not portrait 9:16 media: {asset['asset_id']}")
            _run([
                "ffmpeg", "-hide_banner", "-y", "-stream_loop", "-1", "-i", str(raw),
                "-t", f"{clip_duration:.6f}",
                "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,"
                       "crop=1080:1920,setsar=1,fps=30,format=yuv420p",
                "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                "-pix_fmt", "yuv420p", "-r", "30", str(segment)
            ])
        else:
            raise ValueError(f"Unsupported background media type: {asset.get('media_type')}")

        _, width, height = _probe(segment)
        if (width, height) != (1080, 1920):
            raise ValueError(f"Normalized background segment is not 1080x1920: {segment}")
        segments.append(segment)

    inputs: list[str] = []
    filters: list[str] = []
    for index, segment in enumerate(segments):
        inputs += ["-i", str(segment)]
        filters.append(f"[{index}:v]setpts=PTS-STARTPTS,format=yuv420p[s{index}]")

    current = "s0"
    elapsed = scene_durations[0]
    for index in range(1, len(segments)):
        label = f"x{index}"
        filters.append(
            f"[{current}][s{index}]xfade=transition=fade:duration={transition:.6f}:"
            f"offset={elapsed:.6f}[{label}]"
        )
        current = label
        elapsed += scene_durations[index]

    filters.append(
        f"[{current}]trim=duration={duration:.6f},setpts=PTS-STARTPTS,"
        "fps=30,format=yuv420p[outv]"
    )
    _run([
        "ffmpeg", "-hide_banner", "-y", *inputs, "-filter_complex", ";".join(filters),
        "-map", "[outv]", "-an", "-t", f"{duration:.6f}", "-c:v", "libx264",
        "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-r", "30",
        str(destination)
    ])
    actual, width, height = _probe(destination)
    if (width, height) != (1080, 1920) or actual + 0.10 < duration:
        raise ValueError(
            f"Mixed background reel failed output validation: {width}x{height}, "
            f"{actual:.3f}s for {duration:.3f}s."
        )
    ids = [item["asset_id"] for item in chosen]
    types = [item["media_type"] for item in chosen]
    print("Mixed photo/video background sequence:", list(zip(types, ids)))
    return ids
