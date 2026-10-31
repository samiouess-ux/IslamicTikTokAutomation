"""Prepare audio for every distinct-surah review candidate in one batch.

Downloads exact official verse files, probes each duration, and concatenates
whole consecutive ayahs only. It never trims, time-stretches, or alters audio.
This is a review package, not production approval or publication.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path
from remotezip import RemoteZip

DEFAULT_ARCHIVE = "https://download.qurancomplex.gov.sa/new-sounds/muaiqly-08/hafs/ayat-12-1-2020.zip"
MAX_SECONDS = 65.0


def probe(path: Path) -> float:
    raw = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=nw=1:nk=1", str(path)
    ], text=True).strip()
    value = float(raw)
    if value <= 0:
        raise ValueError(f"Invalid audio duration: {path}")
    return value


def prepare_batch(batch_path: Path, inventory_path: Path, output_dir: Path) -> dict:
    batch = json.loads(batch_path.read_text(encoding="utf-8"))
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    if batch.get("batch_status") != "review_candidates_only":
        raise ValueError("Input must be a review-only Quran candidate batch.")
    if batch.get("rendering_allowed") is not False or batch.get("auto_publish") is not False:
        raise ValueError("Candidate batch safety gates are invalid.")
    if inventory.get("mapped_verse_count") != 6236:
        raise ValueError("A complete official audio inventory is required.")
    members = inventory.get("verses")
    if not isinstance(members, dict):
        raise ValueError("Audio inventory has no verse mapping.")
    output_dir.mkdir(parents=True, exist_ok=True)
    results = []
    with RemoteZip(inventory.get("source_url", DEFAULT_ARCHIVE)) as archive:
        for candidate in batch.get("passages", []):
            surah = int(candidate["surah_number"])
            selected = []
            durations = {}
            files = []
            total = 0.0
            candidate_dir = output_dir / str(candidate["candidate_id"])
            candidate_dir.mkdir(parents=True, exist_ok=True)
            for verse in candidate["verses"]:
                number = int(verse["ayah"])
                key = f"{surah}:{number}"
                member = members.get(key)
                if not member:
                    raise ValueError(f"Official audio mapping missing for {key}")
                target = candidate_dir / f"{surah:03d}_{number:03d}.mp3"
                with archive.open(member) as source, target.open("wb") as dest:
                    shutil.copyfileobj(source, dest)
                duration = probe(target)
                if duration > MAX_SECONDS or total + duration > MAX_SECONDS:
                    target.unlink(missing_ok=True)
                    if not selected:
                        results.append({
                            "candidate_id": candidate["candidate_id"],
                            "surah_number": surah,
                            "status": "blocked_single_ayah_exceeds_65_seconds" if duration > MAX_SECONDS else "blocked_no_complete_ayah_fits",
                            "selected_verses": [],
                            "duration_seconds": 0,
                            "audio_file": None,
                        })
                    break
                selected.append(number)
                durations[number] = round(duration, 3)
                files.append(target)
                total += duration
            if not selected:
                continue
            # Concatenate whole MP3 files in order; stream copy avoids re-encoding.
            list_file = candidate_dir / "concat.txt"
            list_file.write_text("".join(f"file '{p.resolve()}'\n" for p in files), encoding="utf-8")
            combined = candidate_dir / "passage.mp3"
            subprocess.run([
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                "-f", "concat", "-safe", "0", "-i", str(list_file.resolve()),
                "-c", "copy", str(combined.resolve())
            ], check=True)
            actual = probe(combined)
            if actual > MAX_SECONDS:
                raise ValueError(f"Concatenated candidate exceeds 65 seconds: {candidate['candidate_id']}")
            results.append({
                "candidate_id": candidate["candidate_id"],
                "surah_number": surah,
                "status": "audio_prepared_requires_exact_recording_listen_and_user_review",
                "selected_verses": selected,
                "verse_durations_seconds": durations,
                "duration_seconds": round(actual, 3),
                "audio_file": str(combined),
                "archive_members": [members[f"{surah}:{n}"] for n in selected],
                "audio_approved": False,
                "rendering_allowed": False,
                "telegram_delivery": False,
                "auto_publish": False,
            })
    ready = [x for x in results if x["status"].startswith("audio_prepared")]
    if len({x["surah_number"] for x in ready}) != len(ready):
        raise ValueError("Prepared audio batch contains duplicate surahs.")
    report = {
        "status": "multi_surah_audio_review_package_prepared" if len(ready) >= 2 else "insufficient_audio_candidates_prepared",
        "candidate_count": len(batch.get("passages", [])),
        "audio_prepared_count": len(ready),
        "distinct_surah_count": len({x["surah_number"] for x in ready}),
        "maximum_seconds": MAX_SECONDS,
        "audio_processing": "whole_ayah_concat_stream_copy_no_trimming_no_time_stretch",
        "items": results,
        "rendering_allowed": False,
        "telegram_delivery": False,
        "auto_publish": False,
        "manual_review_required": True,
    }
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", type=Path, required=True)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("output/quran_batch_audio"))
    parser.add_argument("--report", type=Path, default=Path("output/quran_batch_audio_report.json"))
    args = parser.parse_args()
    report = prepare_batch(args.batch, args.inventory, args.output_dir)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["audio_prepared_count"] < 2:
        raise SystemExit("Fewer than two distinct-surah audio candidates were prepared.")


if __name__ == "__main__":
    main()
