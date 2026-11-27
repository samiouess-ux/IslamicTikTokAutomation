import importlib.util
import json
import subprocess
from pathlib import Path

from PIL import Image
from quran_word_align.align import mushaf_words

ROOT = Path(".")
AUDIO = ROOT / "test-audio/018.mp3"
BACKGROUND = ROOT / "test-assets/approved-background.mp4"
DATA = json.loads((ROOT / "aligned/018.json").read_text(encoding="utf-8"))
raw = DATA.get("14", DATA.get(14, []))
events = [{"n": int(n), "start": int(s), "end": int(e), "confidence": float(c)}
          for n, s, e, c in raw]
numbers = [event["n"] for event in events]
expected = list(range(1, 16)) + list(range(11, 16)) + list(range(16, 20))
if numbers != expected:
    raise SystemExit(f"Unexpected aligned event sequence: {numbers}")
if any(event["confidence"] < 0.5 for event in events):
    raise SystemExit("Low-confidence alignment event; refusing preview.")

spec = importlib.util.spec_from_file_location(
    "production_quran_renderer", ROOT / "src/render_quran_review_previews.py"
)
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)

mushaf = dict(mushaf_words("hafs")[(18, 14)])
groups = [
    {"name": "opening", "first": 0, "last": 9,
     "arabic": " ".join(mushaf[n] for n in range(1, 11)),
     "english": "And We made firm their hearts when they stood up and said, Our Lord is the Lord of the heavens and the earth."},
    {"name": "repeated_phrase", "first": 10, "last": 19,
     "arabic": " ".join(mushaf[n] for n in range(11, 16)),
     "english": "Never will we invoke besides Him any deity."},
    {"name": "closing", "first": 20, "last": 23,
     "arabic": " ".join(mushaf[n] for n in range(16, 20)),
     "english": "We would have certainly spoken, then, an excessive transgression."},
]
for group in groups:
    group["start_ms"] = events[group["first"]]["start"]
    group["end_ms"] = events[group["last"]]["end"]
if not (groups[0]["end_ms"] <= groups[1]["start_ms"]
        and groups[1]["end_ms"] <= groups[2]["start_ms"]):
    raise SystemExit("Phrase boundaries overlap or are out of order.")

start_ms, end_ms = groups[0]["start_ms"], groups[-1]["end_ms"]
duration = (end_ms - start_ms) / 1000
if duration <= 0 or duration > 30:
    raise SystemExit(f"Unexpected preview duration: {duration}")
font_path = renderer.font_file()
renderer.APPROVED_DESIGN_REFERENCE = ROOT / "references/approved_quran_design.png"
if not renderer.APPROVED_DESIGN_REFERENCE.is_file():
    raise SystemExit("Exact approved Quran design reference is missing.")

out = ROOT / "preview-approved-design"
out.mkdir(exist_ok=True)
verse = {"number": 14, "arabic": " ".join(mushaf[n] for n in range(1, 20)),
         "english": " "}
for index, group in enumerate(groups):
    renderer.make_frame(
        verse, 18, 0, out / f"group{index+1}.png", font_path,
        renderer.SURAH_NAMES_TASHKEEL[17],
        include_surah_header=False,
        arabic_display_text=group["arabic"],
        english_display_text=group["english"],
        show_ayah_number=(index == 0),
    )
renderer.make_intro_frame(
    18, 14, 14, out / "intro.png", font_path,
    renderer.SURAH_NAMES_TASHKEEL[17],
)

filters = [
    "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
    "crop=1080:1920,fps=30,setsar=1[bg]"
]
current = "bg"
for i, group in enumerate(groups, start=1):
    start = (group["start_ms"] - start_ms) / 1000
    end = (group["end_ms"] - start_ms) / 1000
    filters.append(
        f"[{current}][{i+2}:v]overlay=0:0:enable='gte(t,{start:.6f})*lt(t,{end:.6f})'[v{i}]"
    )
    current = f"v{i}"
filters.extend([
    "[5:v]format=rgba,fade=t=out:st=0.4:d=0.8:alpha=1[intro]",
    f"[{current}][intro]overlay=0:0:format=auto[vout]"
])
cmd = [
    "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
    "-stream_loop", "-1", "-i", str(BACKGROUND),
    "-ss", f"{start_ms/1000:.3f}", "-t", f"{duration:.3f}", "-i", str(AUDIO),
    "-loop", "1", "-framerate", "30", "-i", str(out / "group1.png"),
    "-loop", "1", "-framerate", "30", "-i", str(out / "group2.png"),
    "-loop", "1", "-framerate", "30", "-i", str(out / "group3.png"),
    "-loop", "1", "-framerate", "30", "-i", str(out / "intro.png"),
    "-filter_complex", ";".join(filters),
    "-map", "[vout]", "-map", "1:a:0", "-t", f"{duration:.3f}",
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
    "-movflags", "+faststart", "quran-18-14-approved-design-sync-preview.mp4"
]
subprocess.run(cmd, check=True)
report = {
    "status": "isolated_approved_design_sync_preview",
    "surah_ayah": "18:14",
    "reciter": "Maher Al-Muaiqly",
    "duration_seconds": round(duration, 3),
    "event_count": len(events),
    "repeat_count": 2,
    "repeated_phrase_word_numbers": list(range(11, 16)),
    "groups": [{"name": g["name"], "start_seconds": round((g["start_ms"]-start_ms)/1000, 3),
                "end_seconds": round((g["end_ms"]-start_ms)/1000, 3),
                "arabic": g["arabic"], "english": g["english"]} for g in groups],
    "approved_reference_used": str(renderer.APPROVED_DESIGN_REFERENCE),
    "production_modified": False,
    "telegram_delivery": False,
    "cron_triggered": False,
    "auto_publish": False,
    "human_audio_visual_review_required": True
}
(ROOT / "quran-18-14-approved-design-sync-report.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps(report, ensure_ascii=False))
