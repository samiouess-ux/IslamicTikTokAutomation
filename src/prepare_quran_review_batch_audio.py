"""Prepare audio for every distinct-surah review candidate in one batch.

Downloads exact official verse files, trims only detected leading/trailing
silence with a safety margin, and stream-copies the MP3 recitation. Internal
recitation and whole-ayah order remain untouched. This is a review package,
not production approval or publication.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path
from remotezip import RemoteZip

DEFAULT_ARCHIVE = "https://download.qurancomplex.gov.sa/new-sounds/muaiqly-08/hafs/ayat-12-1-2020.zip"
MIN_SECONDS = 0.0
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



def trim_edge_silence(source: Path, destination: Path, source_duration: float,
                      keep_seconds: float = 0.12) -> float:
    """Remove only detected leading/trailing silence; preserve MP3 frames and inner recitation."""
    detection = subprocess.run([
        "ffmpeg", "-hide_banner", "-i", str(source),
        "-af", "silencedetect=noise=-50dB:d=0.25",
        "-f", "null", "-"
    ], capture_output=True, text=True)
    if detection.returncode != 0:
        raise RuntimeError(f"Unable to inspect edge silence in {source}: {detection.stderr[-1000:]}")

    starts = [float(value) for value in re.findall(
        r"silence_start:\s*([0-9.]+)", detection.stderr
    )]
    ends = [float(value) for value in re.findall(
        r"silence_end:\s*([0-9.]+)", detection.stderr
    )]
    trim_start = 0.0
    trim_end = source_duration

    if starts and ends and starts[0] <= 0.05:
        trim_start = max(0.0, ends[0] - keep_seconds)
    if starts and ends and ends[-1] >= source_duration - 0.08:
        trim_end = min(source_duration, starts[-1] + keep_seconds)

    destination.parent.mkdir(parents=True, exist_ok=True)
    if trim_start <= 0.02 and trim_end >= source_duration - 0.02:
        shutil.copyfile(source, destination)
        return source_duration
    if trim_end - trim_start < 0.5:
        raise ValueError(f"Edge-silence detection left too little recitation in {source}")

    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-ss", f"{trim_start:.3f}", "-i", str(source),
        "-t", f"{trim_end - trim_start:.3f}",
        "-map", "0:a:0", "-c:a", "copy", "-avoid_negative_ts", "make_zero",
        str(destination)
    ], check=True)
    processed_duration = probe(destination)
    if processed_duration <= 0 or processed_duration > source_duration + 0.10:
        raise ValueError(f"Unexpected duration after edge-silence handling: {destination}")
    return processed_duration


def prepare_batch(batch_path: Path, inventory_path: Path, output_dir: Path, target_count: int = 3) -> dict:
    batch = json.loads(batch_path.read_text(encoding="utf-8"))
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    if not isinstance(target_count, int) or target_count < 1:
        raise ValueError("target_count must be a positive integer.")
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
            if sum(item["status"].startswith("audio_prepared") for item in results) >= target_count:
                break
            surah = int(candidate["surah_number"])
            selected = []
            durations = {}
            processed_durations = {}
            removed_edge_silence = {}
            processed_audio_files = {}
            files = []
            total = 0.0
            candidate_dir = output_dir / str(candidate["candidate_id"])
            candidate_dir.mkdir(parents=True, exist_ok=True)
            blocked_reason = None
            # Probe consecutive whole ayahs in order. Keep the longest prefix
            # whose measured source duration fits the 65-second limit. A short
            # surah naturally remains whole when its complete duration fits.
            # Keep the complete source request, even when the 65-second cap
            # means only a contiguous prefix can be selected for this video.
            requested = [int(verse["ayah"]) for verse in candidate["verses"]]
            for verse in candidate["verses"]:
                number = int(verse["ayah"])
                key = f"{surah}:{number}"
                member = members.get(key)
                if not member:
                    raise ValueError(f"Official audio mapping missing for {key}")
                target = candidate_dir / f"{surah:03d}_{number:03d}.mp3"
                with archive.open(member) as source, target.open("wb") as dest:
                    shutil.copyfileobj(source, dest)
                source_duration = probe(target)
                processed_target = candidate_dir / "processed" / f"{surah:03d}_{number:03d}.mp3"
                processed_duration = trim_edge_silence(target, processed_target, source_duration)
                proposed_total = total + processed_duration
                if processed_duration > MAX_SECONDS and not selected:
                    target.unlink(missing_ok=True)
                    processed_target.unlink(missing_ok=True)
                    blocked_reason = "blocked_single_ayah_exceeds_65_seconds"
                    break
                if proposed_total > MAX_SECONDS:
                    target.unlink(missing_ok=True)
                    processed_target.unlink(missing_ok=True)
                    break
                selected.append(number)
                durations[number] = round(source_duration, 3)
                processed_durations[number] = round(processed_duration, 3)
                removed_edge_silence[str(number)] = round(source_duration - processed_duration, 3)
                processed_audio_files[str(number)] = str(processed_target)
                files.append(processed_target)
                total = proposed_total

            if not selected:
                results.append({
                    "candidate_id": candidate["candidate_id"],
                    "surah_number": surah,
                    "status": blocked_reason or "blocked_no_complete_ayah_range_under_65_seconds",
                    "requested_verses": requested,
                    "verse_durations_seconds": durations,
                    "processed_verse_durations_seconds": processed_durations,
                    "edge_silence_removed_seconds": removed_edge_silence,
                    "complete_duration_seconds": round(total, 3),
                    "selected_verses": [],
                    "remaining_verses": requested,
                    "passage_complete": False,
                    "continuation_policy": "retry_same_first_unconfirmed_ayahs_until_confirmed_delivery",
                    "duration_seconds": 0,
                    "audio_file": None,
                    "audio_approved": False,
                    "rendering_allowed": False,
                    "telegram_delivery": False,
                    "auto_publish": False,
                })
                continue
            if total <= 0:
                results.append({
                    "candidate_id": candidate["candidate_id"],
                    "surah_number": surah,
                    "status": "blocked_no_complete_ayah_range_under_65_seconds",
                    "requested_verses": requested,
                    "verse_durations_seconds": durations,
                    "processed_verse_durations_seconds": processed_durations,
                    "edge_silence_removed_seconds": removed_edge_silence,
                    "complete_duration_seconds": round(total, 3),
                    "selected_verses": [],
                    "duration_seconds": 0,
                    "audio_file": None,
                    "audio_approved": False,
                    "rendering_allowed": False,
                    "telegram_delivery": False,
                    "auto_publish": False,
                })
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
            if actual > MAX_SECONDS or actual <= 0:
                raise ValueError(
                    f"Concatenated candidate duration {actual:.3f}s is outside "
                    f"0-65 seconds: {candidate['candidate_id']}"
                )
            results.append({
                "candidate_id": candidate["candidate_id"],
                "surah_number": surah,
                "status": "audio_prepared_requires_exact_recording_listen_and_user_review",
                "requested_verses": requested,
                "selected_verses": selected,
                "remaining_verses": requested[len(selected):],
                "passage_complete": len(selected) == len(requested),
                "continuation_policy": "retry_same_first_unconfirmed_ayahs_until_confirmed_delivery",
                "verse_durations_seconds": durations,
                "processed_verse_durations_seconds": processed_durations,
                "edge_silence_removed_seconds": removed_edge_silence,
                "inter_verse_silence_seconds": 0.24,
                "processed_audio_files": processed_audio_files,
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
        "status": "audio_review_package_prepared" if len(ready) >= target_count else "insufficient_audio_candidates_prepared",
        "candidate_count": len(batch.get("passages", [])),
        "target_count": target_count,
        "audio_prepared_count": len(ready),
        "distinct_surah_count": len({x["surah_number"] for x in ready}),
        "minimum_seconds": MIN_SECONDS,
        "maximum_seconds": MAX_SECONDS,
        "audio_processing": "longest_contiguous_whole_ayah_prefix_up_to_65_seconds_with_edge_only_silence_detection_and_mp3_stream_copy",
        "continuation_policy": "Unselected ayahs remain explicitly listed and are not marked used. The next batch starts again at the first ayah absent from confirmed delivery history; only confirmed delivery advances the sequence.",
        "edge_silence_policy": "silencedetect at -50dB for 0.25s; retain 0.12s guard at each detected file edge; never remove internal silence or trim recitation",
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
    parser.add_argument("--target-count", type=int, default=3)
    args = parser.parse_args()
    report = prepare_batch(args.batch, args.inventory, args.output_dir, args.target_count)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["audio_prepared_count"] != args.target_count:
        raise SystemExit(f"Expected exactly {args.target_count} distinct-surah audio candidates; prepared {report['audio_prepared_count']}.")


if __name__ == "__main__":
    main()
