import csv
import gzip
import math
from array import array
import hashlib
import json
import subprocess
import tempfile
import urllib.request
import zipfile
from pathlib import Path

BASE = "https://github.com/QUD-Technologies/quranic-universal-audio/releases/download/v4.0.0"
SLUG = "saad_al_ghamdi_tarteel"
SURAHS = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 18, 19, 20, 21, 24, 25, 26, 27, 28, 29, 30, 31, 32, 36, 38, 50, 55, 59, 67, 73, 78, 87, 103, 109, 112, 113, 114)
# Project owner listened to these exact intervals and confirmed they are correct.
# This records review provenance only; it does not alter audio or timestamps.
USER_CONFIRMED_LISTENING = {'1:1', '1:5', '38:1', '38:88', '67:9', '67:12'}
SAMPLE_RATE = 16000
WINDOW_MS = 100
SILENCE_RMS_THRESHOLD = 100  # about -50 dBFS for signed 16-bit PCM

def fetch(url, path):
    req = urllib.request.Request(url, headers={"User-Agent": "QuranAudioTimingDiagnostic/1.0"})
    with urllib.request.urlopen(req, timeout=90) as response, path.open("wb") as out:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)

with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    manifest_path, catalog_path = root / "manifest.json", root / "catalog.json"
    fetch(f"{BASE}/manifest.json", manifest_path)
    fetch(f"{BASE}/catalog.json", catalog_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    entry = manifest["recitations"][SLUG]
    archive_path = root / entry["zip"]
    fetch(entry["zip_url"], archive_path)
    actual_sha = hashlib.sha256(archive_path.read_bytes()).hexdigest()
    if actual_sha != entry["sha256"]:
        raise SystemExit(f"ZIP_SHA256_MISMATCH expected={entry['sha256']} actual={actual_sha}")
    print(f"ZIP_SHA256_OK {actual_sha}")

    with zipfile.ZipFile(archive_path) as archive:
        names = set(archive.namelist())
        required = {"catalog.json", "verse_timestamps.json.gz"}
        if not required.issubset(names):
            raise SystemExit(f"ZIP_MISSING_FILES {sorted(required - names)}")
        reciter = json.loads(archive.read("catalog.json"))
        payload = json.loads(gzip.decompress(archive.read("verse_timestamps.json.gz")))

    if reciter.get("slug") != SLUG:
        raise SystemExit(f"WRONG_RECITER {reciter.get('slug')}")
    if str(reciter.get("riwayah", "")).lower() not in {"hafs", "hafs_an_asim"}:
        raise SystemExit(f"WRONG_RIWAYAH {reciter.get('riwayah')}")
    if str(reciter.get("channel", "")).lower() not in {"tarteel", "tarteel cdn"}:
        raise SystemExit(f"WRONG_AUDIO_CHANNEL {reciter.get('channel')}")
    rows = payload.get("rows", [])
    if not rows:
        raise SystemExit("EMPTY_VERSE_TIMESTAMP_ROWS")

    source = next((x for x in catalog.get("recitations", []) if x.get("slug") == SLUG), None)
    if not source:
        raise SystemExit("RECITATION_MISSING_FROM_RELEASE_CATALOG")
    urls = source.get("audio", {}).get("chapter_urls", {})
    if not urls:
        raise SystemExit("SOURCE_AUDIO_URLS_MISSING")
    print(f"RIWAYAH {reciter.get('riwayah')}")
    print(f"TIMESTAMP_ROWS {len(rows)}")
    print(f"DECLARED_COVERAGE {source.get('coverage', {}).get('ayahs')}")
    print(f"SOURCE_CHANNEL {source.get('channel')}")
    # Validate the complete canonical verse-timing index.
    canonical = {}
    malformed = []
    for index, row in enumerate(rows):
        if not isinstance(row, list) or len(row) < 4:
            malformed.append(index)
            continue
        verse_key = str(row[0])
        try:
            start_ms, end_ms = int(row[1]), int(row[2])
        except (TypeError, ValueError):
            malformed.append(index)
            continue
        if start_ms < 0 or end_ms <= start_ms:
            malformed.append(index)
            continue
        if bool(row[3]):
            if verse_key in canonical:
                raise SystemExit(f"DUPLICATE_CANONICAL_VERSE_TIMESTAMP {verse_key}")
            canonical[verse_key] = (start_ms, end_ms)
    if malformed:
        raise SystemExit(f"MALFORMED_TIMESTAMP_ROWS count={len(malformed)} first={malformed[:10]}")
    declared = int(source.get("coverage", {}).get("ayahs") or 0)
    print(f"CANONICAL_VERSE_KEYS {len(canonical)}")
    print(f"MALFORMED_TIMESTAMP_ROWS {len(malformed)}")
    print(f"DECLARED_COVERAGE_MATCH {len(canonical) == declared}")
    if declared and len(canonical) != declared:
        raise SystemExit(f"CANONICAL_COVERAGE_MISMATCH declared={declared} actual={len(canonical)}")
    # Validate timestamp order across every canonical surah, not only the
    # three chapters whose audio files are downloaded below.
    previous_start_by_surah = {}
    for row in rows:
        if not bool(row[3]):
            continue
        parts = str(row[0]).split(":")
        if len(parts) != 2 or not all(part.isdigit() for part in parts):
            raise SystemExit(f"INVALID_CANONICAL_VERSE_KEY {row[0]}")
        surah_number = int(parts[0])
        start_ms = int(row[1])
        previous_start = previous_start_by_surah.get(surah_number)
        if previous_start is not None and start_ms < previous_start:
            raise SystemExit(
                f"NON_MONOTONIC_CANONICAL_SOURCE_ORDER_SURAH_{surah_number:03d}"
            )
        previous_start_by_surah[surah_number] = start_ms
    print(f"ALL_SURAHS_CANONICAL_START_ORDER_CHECK PASS {len(previous_start_by_surah)}")
    # Audit interval-end ordering and adjacent overlap for every canonical
    # ayah. These are reported as diagnostics rather than assumed defects.
    canonical_by_surah = {}
    for row in rows:
        if bool(row[3]):
            chapter = int(str(row[0]).split(":")[0])
            canonical_by_surah.setdefault(chapter, []).append(
                (str(row[0]), int(row[1]), int(row[2]))
            )
    end_order_issues = []
    overlap_issues = []
    for chapter, intervals in canonical_by_surah.items():
        intervals.sort(key=lambda item: item[1])
        for previous, current in zip(intervals, intervals[1:]):
            if current[2] < previous[2]:
                end_order_issues.append((chapter, previous[0], current[0]))
            if current[1] < previous[2]:
                overlap_issues.append((
                    chapter, previous[0], current[0],
                    previous[2] - current[1]
                ))
    print(f"ALL_SURAHS_CANONICAL_INTERVAL_END_ORDER_ISSUES {len(end_order_issues)}")
    print(f"ALL_SURAHS_ADJACENT_INTERVAL_OVERLAPS {len(overlap_issues)}")
    for issue in end_order_issues[:20]:
        print(f"INTERVAL_END_ORDER_REVIEW surah={issue[0]} pair={issue[1]},{issue[2]}")
    for issue in overlap_issues[:20]:
        print(
            f"INTERVAL_OVERLAP_REVIEW surah={issue[0]} "
            f"pair={issue[1]},{issue[2]} overlap_ms={issue[3]}"
        )

    surah_counts = {}
    for key in canonical:
        parts = key.split(":")
        if len(parts) != 2 or not all(part.isdigit() for part in parts):
            raise SystemExit(f"INVALID_CANONICAL_VERSE_KEY {key}")
        surah_counts[int(parts[0])] = surah_counts.get(int(parts[0]), 0) + 1
    print(f"CANONICAL_SURAH_COUNT {len(surah_counts)}")
    print(f"CANONICAL_SURAH_RANGE {min(surah_counts)}-{max(surah_counts)}")
    # Verify that each surah's canonical ayah keys form a gap-free sequence
    # beginning at verse 1, and that the 114 surah numbers are contiguous.
    verse_numbers_by_surah = {}
    for key in canonical:
        surah_text, ayah_text = key.split(":")
        verse_numbers_by_surah.setdefault(int(surah_text), []).append(int(ayah_text))
    missing_or_gapped_surahs = []
    for chapter, verse_numbers in verse_numbers_by_surah.items():
        ordered_numbers = sorted(verse_numbers)
        expected_numbers = list(range(1, len(ordered_numbers) + 1))
        if ordered_numbers != expected_numbers:
            missing_or_gapped_surahs.append(chapter)
    expected_surahs = list(range(1, 115))
    actual_surahs = sorted(verse_numbers_by_surah)
    print(f"CANONICAL_SURAH_SEQUENCE_CHECK {'PASS' if actual_surahs == expected_surahs else 'FAIL'}")
    print(f"CANONICAL_AYAH_NUMBER_CONTINUITY_CHECK {'PASS' if not missing_or_gapped_surahs else 'FAIL'}")
    if actual_surahs != expected_surahs or missing_or_gapped_surahs:
        raise SystemExit(
            f"CANONICAL_KEY_SEQUENCE_MISMATCH surah_sequence_ok={actual_surahs == expected_surahs} "
            f"gapped_surahs={missing_or_gapped_surahs[:20]}"
        )

    review_candidates = []
    for surah in SURAHS:
        chapter = str(surah)
        url = urls.get(chapter)
        if not url or not url.startswith("https://"):
            raise SystemExit(f"SOURCE_URL_MISSING_SURAH_{surah:03d}")
        chapter_rows = [row for row in rows if str(row[0]).split(":")[0] == chapter and bool(row[3])]
        if not chapter_rows:
            raise SystemExit(f"CANONICAL_TIMESTAMPS_MISSING_SURAH_{surah:03d}")
        # Keep the timestamps paired with the exact chapter audio declared by QUA.
        starts = [int(row[1]) for row in chapter_rows]
        if starts != sorted(starts):
            raise SystemExit(f"NON_MONOTONIC_AYAH_STARTS_SURAH_{surah:03d}")
        last_end_ms = max(int(row[2]) for row in chapter_rows)
        audio_path = root / f"surah-{surah:03d}.audio"
        fetch(url, audio_path)
        if audio_path.stat().st_size < 10000:
            raise SystemExit(f"SOURCE_AUDIO_TOO_SMALL_SURAH_{surah:03d}")
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(audio_path)],
            check=True, capture_output=True, text=True,
        )
        duration = float(probe.stdout.strip())
        # Every canonical ayah interval must fit inside its matched source chapter.
        duration_ms = round(duration * 1000)
        out_of_bounds = [
            str(row[0]) for row in chapter_rows
            if int(row[1]) < 0 or int(row[2]) > duration_ms + 1000
        ]
        if out_of_bounds:
            raise SystemExit(
                f"TIMESTAMP_OUTSIDE_SOURCE_AUDIO_SURAH_{surah:03d}: {out_of_bounds[:10]}"
            )
        decode = subprocess.run(
            ["ffmpeg", "-v", "error", "-i", str(audio_path), "-f", "null", "-"],
            capture_output=True, text=True,
        )
        if decode.returncode:
            raise SystemExit(f"AUDIO_DECODE_FAILED_SURAH_{surah:03d}: {decode.stderr[-1000:]}")

        # Acoustic screening only: measure signal energy inside each canonical
        # interval. This flags suspiciously silent edges/intervals; it does not
        # identify words or prove phonetic alignment.
        pcm = subprocess.run(
            ["ffmpeg", "-v", "error", "-i", str(audio_path), "-f", "s16le",
             "-ac", "1", "-ar", str(SAMPLE_RATE), "pipe:1"],
            check=True, capture_output=True,
        ).stdout
        samples = array("h")
        samples.frombytes(pcm)
        if __import__("sys").byteorder != "little":
            samples.byteswap()

        def window_rms_db(start_sample, end_sample):
            chunk = samples[max(0, start_sample):min(len(samples), end_sample)]
            if not chunk:
                return -120.0
            mean_square = sum(value * value for value in chunk) / len(chunk)
            if mean_square <= 0:
                return -120.0
            return 20.0 * math.log10(math.sqrt(mean_square) / 32768.0)

        report_path = Path("saad_acoustic_probe.csv")
        write_header = not report_path.exists()
        with report_path.open("a", newline="", encoding="utf-8") as report_file:
            writer = csv.writer(report_file)
            if write_header:
                writer.writerow([
                    "surah", "ayah_key", "start_ms", "end_ms",
                    "first_200ms_rms_dbfs", "last_200ms_rms_dbfs",
                    "silent_100ms_windows_pct", "human_listening_review_status"
                ])
            for row in chapter_rows:
                start_ms, end_ms = int(row[1]), int(row[2])
                start_sample = round(start_ms * SAMPLE_RATE / 1000)
                end_sample = round(end_ms * SAMPLE_RATE / 1000)
                first_db = window_rms_db(
                    start_sample, min(end_sample, start_sample + SAMPLE_RATE // 5)
                )
                last_db = window_rms_db(
                    max(start_sample, end_sample - SAMPLE_RATE // 5), end_sample
                )
                total_windows = max(1, math.ceil((end_sample - start_sample) / (SAMPLE_RATE * WINDOW_MS / 1000)))
                silent_windows = 0
                window_samples = SAMPLE_RATE * WINDOW_MS // 1000
                for offset in range(start_sample, end_sample, window_samples):
                    if window_rms_db(offset, min(end_sample, offset + window_samples)) < (
                        20.0 * math.log10(SILENCE_RMS_THRESHOLD / 32768.0)
                    ):
                        silent_windows += 1
                silent_pct = round(100.0 * silent_windows / total_windows, 2)
                if first_db < -50.0 or last_db < -50.0 or silent_pct >= 25.0:
                    review_candidates.append({
                        "ayah": row[0],
                        "start_ms": start_ms,
                        "end_ms": end_ms,
                        "first_dbfs": round(first_db, 2),
                        "last_dbfs": round(last_db, 2),
                        "silent_windows_pct": silent_pct,
                        "review_status": "USER_CONFIRMED_CORRECT" if str(row[0]) in USER_CONFIRMED_LISTENING else "LISTENING_NOT_RECORDED",
                    })
                writer.writerow([
                    surah, row[0], start_ms, end_ms,
                    round(first_db, 2), round(last_db, 2), silent_pct,
                    "USER_CONFIRMED_CORRECT" if str(row[0]) in USER_CONFIRMED_LISTENING else "NOT_REVIEWED"
                ])
        print(f"SURAH_{surah:03d}_ACOUSTIC_INTERVALS_SCREENED {len(chapter_rows)}")

        print(
            f"SURAH_{surah:03d} bytes={audio_path.stat().st_size} "
            f"duration={duration:.3f}s last_ayah_end={last_end_ms/1000:.3f}s "
            f"tail_delta={duration-last_end_ms/1000:+.3f}s decode=OK"
        )

print(f"ACOUSTIC_ENERGY_SCREENING_COMPLETE selected_surahs={len(SURAHS)}")
print(f"ACOUSTIC_REVIEW_CANDIDATE_COUNT {len(review_candidates)}")
for candidate in review_candidates:
    print(
        "ACOUSTIC_REVIEW_CANDIDATE "
        f"{candidate['ayah']} start_ms={candidate['start_ms']} "
        f"end_ms={candidate['end_ms']} "
        f"first_dbfs={candidate['first_dbfs']} "
        f"last_dbfs={candidate['last_dbfs']} "
        f"silent_windows_pct={candidate['silent_windows_pct']} "
        f"human_review={candidate.get('review_status', 'NOT_RECORDED')}"
    )
# Produce direct seek links for every acoustic candidate, including newly
# screened surahs. User-confirmed intervals retain their review provenance.
review_path = Path("saad_human_listening_review.md")
with review_path.open("w", encoding="utf-8") as review_file:
    review_file.write("# Saad Al-Ghamdi — matched-source listening review\\n\\n")
    review_file.write("These links open the exact QUA source chapter and request playback at each flagged ayah interval. Browser/player support for media time fragments may vary; if seeking is unsupported, use the listed start/end times manually.\\n\\n")
    for candidate in review_candidates:
        surah_text, ayah_text = candidate["ayah"].split(":")
        surah = int(surah_text)
        label = f"Surah {surah}, ayah {ayah_text}"
        start_ms, end_ms = candidate["start_ms"], candidate["end_ms"]
        audio_url = urls[str(surah)]
        status = candidate.get("review_status", "NOT_REVIEWED")
        review_file.write(
            f"- **{label}** — {start_ms/1000:.3f}s to {end_ms/1000:.3f}s "
            f"— {status}: [source audio]({audio_url}#t={start_ms/1000:.3f},{end_ms/1000:.3f})\\n"
        )
print(f"HUMAN_LISTENING_REVIEW_LINKS_WRITTEN {review_path}")
print("USER_CONFIRMED_LISTENING_CANDIDATES " + str(sum(item["ayah"] in USER_CONFIRMED_LISTENING for item in review_candidates)))
print("UNREVIEWED_ACOUSTIC_CANDIDATES " + str(sum(item["ayah"] not in USER_CONFIRMED_LISTENING for item in review_candidates)))
print("Acoustic thresholds remain screening flags; user-confirmed clips are recorded as reviewed, not defects.")
print("MATCHED_SOURCE_TIMESTAMP_BOUNDS_CHECK PASS")
print("This validates interval structure and source-audio bounds, not acoustic word-level alignment.")
