"""Build a review-only per-ayah URL inventory for Saad Al-Ghamdi.

EveryAyah/Maqra documents the upstream folder as Ghamadi_40kbps and the
canonical filename format as SSSAAA.mp3. This creates URL references only:
it does not download audio, verify checksums, grant rights, or approve use.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

SOURCE_BASE = "https://everyayah.com/data/Ghamadi_40kbps/"
SURAH_VERSE_COUNTS = [
    7, 286, 200, 176, 120, 165, 206, 75, 129, 109, 123, 111, 43, 52,
    99, 128, 111, 110, 98, 135, 112, 78, 118, 64, 77, 227, 93, 88,
    69, 60, 34, 30, 73, 54, 45, 83, 182, 88, 75, 85, 54, 53, 89,
    59, 37, 35, 38, 29, 18, 45, 60, 49, 62, 55, 78, 96, 29, 22,
    24, 13, 14, 11, 11, 18, 12, 12, 30, 52, 52, 44, 28, 28, 20,
    56, 40, 31, 50, 40, 46, 42, 29, 19, 36, 25, 22, 17, 19, 26,
    30, 20, 15, 21, 11, 8, 8, 19, 5, 8, 8, 11, 11, 8, 3, 9, 5,
    4, 7, 3, 6, 3, 5, 4, 5, 6,
]
EXPECTED_VERSES = 6236


def build_inventory() -> dict:
    if len(SURAH_VERSE_COUNTS) != 114 or sum(SURAH_VERSE_COUNTS) != EXPECTED_VERSES:
        raise RuntimeError("Canonical Quran surah/ayah count table is invalid.")

    verses = {}
    for surah, count in enumerate(SURAH_VERSE_COUNTS, start=1):
        for ayah in range(1, count + 1):
            key = f"{surah}:{ayah}"
            filename = f"{surah:03d}{ayah:03d}.mp3"
            verses[key] = f"{SOURCE_BASE}{filename}"

    if len(verses) != EXPECTED_VERSES:
        raise RuntimeError(f"Expected {EXPECTED_VERSES} ayah URLs, got {len(verses)}.")

    return {
        "source_type": "per_ayah_http",
        "source_name": "EveryAyah Ghamadi_40kbps (Saad Al-Ghamdi)",
        "source_url_template": f"{SOURCE_BASE}{{SSS}}{{AAA}}.mp3",
        "reciter_name": "Saad Al-Ghamdi",
        "riwayah": "Hafs 'an Asim",
        "expected_verse_count": EXPECTED_VERSES,
        "mapped_verse_count": len(verses),
        "mapping_status": "url_pattern_enumerated_not_network_verified",
        "recording_rights_status": "unverified_written_permission_required",
        "rights_verified": False,
        "commercial_use_allowed": False,
        "audio_approved": False,
        "rendering_allowed": False,
        "telegram_delivery": False,
        "auto_publish": False,
        "verses": verses,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("output/saad_ghamdi_audio_inventory.json"))
    args = parser.parse_args()
    inventory = build_inventory()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Created {inventory['mapped_verse_count']} Saad Al-Ghamdi per-ayah URL references: {args.output}")
    print("No audio rights or production approval are implied.")


if __name__ == "__main__":
    main()
