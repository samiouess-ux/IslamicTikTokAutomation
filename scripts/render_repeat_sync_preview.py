import json
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

AUDIO = Path("test-audio/018.mp3")
DATA = json.loads(Path("aligned/018.json").read_text(encoding="utf-8"))
raw = DATA.get("14", DATA.get(14, []))
from quran_word_align.align import mushaf_words
mushaf = dict(mushaf_words("hafs")[(18, 14)])
events = [
    {"n": int(n), "start": int(s), "end": int(e), "confidence": float(c)}
    for n, s, e, c in raw
]
numbers = [e["n"] for e in events]
expected_sequence = list(range(1, 16)) + list(range(11, 16)) + list(range(16, 20))
if numbers != expected_sequence:
    raise SystemExit(f"Unexpected aligned event sequence for 18:14: {numbers}")

# Keep the repeated phrase on screen for both recitations.
first_11 = next(i for i, e in enumerate(events) if e["n"] == 11)
second_11 = next(i for i, e in enumerate(events[first_11 + 1:], first_11 + 1) if e["n"] == 11)
second_15 = next(i for i, e in enumerate(events[second_11:], second_11) if e["n"] == 15)
first_16 = next(i for i, e in enumerate(events) if e["n"] == 16)
if not (first_11 < second_11 <= second_15 < first_16):
    raise SystemExit("Repeated phrase boundaries are not in canonical order.")

groups = [
    {"name": "opening", "first": 0, "last": first_11 - 1,
     "english": "And We made firm their hearts when they stood up and said, Our Lord is the Lord of the heavens and the earth."},
    {"name": "repeated_phrase", "first": first_11, "last": second_15,
     "english": "Never will we invoke besides Him any deity."},
    {"name": "closing", "first": first_16, "last": len(events) - 1,
     "english": "We would have certainly spoken, then, an excessive transgression."},
]
for group in groups:
    group["start_ms"] = events[group["first"]]["start"]
    group["end_ms"] = events[group["last"]]["end"]
    group["arabic"] = " ".join(mushaf[events[i]["n"]] for i in range(group["first"], group["last"] + 1)
                               if i < len(events) and events[i]["n"] not in range(11, 16) or
                               group["name"] == "repeated_phrase")
# For the repeated phrase, show its canonical words once, while timing spans both recitations.
groups[1]["arabic"] = " ".join(mushaf[n] for n in range(11, 16))
groups[0]["arabic"] = " ".join(mushaf[n] for n in range(1, 11))
groups[2]["arabic"] = " ".join(mushaf[n] for n in range(16, 20))

start_ms = groups[0]["start_ms"]
end_ms = groups[2]["end_ms"]
duration = (end_ms - start_ms) / 1000
if duration <= 0 or duration > 30:
    raise SystemExit(f"Unexpected preview duration: {duration}")

font_path = subprocess.check_output(["fc-match", "-f", "%{file}", "Amiri"], text=True).strip()
if not Path(font_path).is_file():
    raise SystemExit("Amiri font unavailable.")
Path("preview").mkdir(exist_ok=True)

def wrap_arabic(draw, text, font, max_width):
    lines, current = [], ""
    for word in text.split():
        candidate = (current + " " + word).strip()
        if draw.textbbox((0, 0), candidate, font=font, direction="rtl", language="ar")[2] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines

for index, group in enumerate(groups):
    im = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    label_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 26)
    arabic_font = ImageFont.truetype(font_path, 78, layout_engine=ImageFont.Layout.RAQM)
    english_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 34)
    draw.text((540, 240), "TIMING TEST ONLY  •  18:14", font=label_font, fill=(224, 194, 132, 255), anchor="mm")
    lines = wrap_arabic(draw, group["arabic"], arabic_font, 920)
    y = 760 - (len(lines) - 1) * 66
    for line in lines:
        draw.text((540, y), line, font=arabic_font, fill=(255, 255, 255, 255),
                  anchor="mm", direction="rtl", language="ar")
        y += 132
    english_lines = {
        "opening": ["And We made firm their hearts when they stood up", "and said, Our Lord is the Lord of the heavens and the earth."],
        "repeated_phrase": ["Never will we invoke besides Him any deity."],
        "closing": ["We would have certainly spoken, then,", "an excessive transgression."]
    }[group["name"]]
    ey = 1160
    for line in english_lines:
        draw.text((540, ey), line, font=english_font, fill=(225, 220, 207, 255), anchor="mm")
        ey += 54
    im.save(f"preview/group{index+1}.png")

local = []
for group in groups:
    local.append({
        "name": group["name"],
        "start": (group["start_ms"] - start_ms) / 1000,
        "end": (group["end_ms"] - start_ms) / 1000,
        "arabic": group["arabic"],
        "english": group["english"],
    })

filter_complex = (
    f"[0:v][2:v]overlay=0:0:enable='between(t,{local[0]['start']:.3f},{local[0]['end']:.3f})'[v1];"
    f"[v1][3:v]overlay=0:0:enable='between(t,{local[1]['start']:.3f},{local[1]['end']:.3f})'[v2];"
    f"[v2][4:v]overlay=0:0:enable='between(t,{local[2]['start']:.3f},{local[2]['end']:.3f})'[v]"
)
cmd = [
    "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
    "-f", "lavfi", "-i", f"color=c=0x102b32:s=1080x1920:r=30:d={duration:.3f}",
    "-ss", f"{start_ms/1000:.3f}", "-t", f"{duration:.3f}", "-i", str(AUDIO),
    "-loop", "1", "-i", "preview/group1.png",
    "-loop", "1", "-i", "preview/group2.png",
    "-loop", "1", "-i", "preview/group3.png",
    "-filter_complex", filter_complex,
    "-map", "[v]", "-map", "1:a:0", "-t", f"{duration:.3f}",
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
    "-movflags", "+faststart", "quran-18-14-repeat-sync-preview.mp4"
]
subprocess.run(cmd, check=True)

report = {
    "status": "isolated_review_only_sync_preview",
    "surah_ayah": "18:14",
    "reciter": "Maher Al-Muaiqly",
    "audio_crop_start_ms": start_ms,
    "audio_crop_end_ms": end_ms,
    "duration_seconds": round(duration, 3),
    "events": len(events),
    "expected_event_sequence_verified": True,
    "repeated_phrase_word_numbers": list(range(11, 16)),
    "repeat_count": 2,
    "groups": local,
    "production_modified": False,
    "telegram_delivery": False,
    "auto_publish": False,
    "note": "Technical synchronization preview only. It uses a neutral test background, not the approved production design. Listening and visual review are still required before integration."
}
Path("quran-18-14-repeat-sync-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({k: report[k] for k in ("status","surah_ayah","duration_seconds","events","repeat_count","groups")}, ensure_ascii=False))
