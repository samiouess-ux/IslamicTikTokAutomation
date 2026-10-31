"""Inspect the official King Fahd Complex verse archive and map every verse.

This produces an inventory only. It does not assert translation correctness or
reuse permission for any item; those checks remain separate gates.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from remotezip import RemoteZip

ARCHIVE_URL = "https://download.qurancomplex.gov.sa/new-sounds/muaiqly-08/hafs/ayat-12-1-2020.zip"
ENTRY_RE = re.compile(r"(?:^|/)10-(\d{3})(\d{3})-A08\.mp3$", re.IGNORECASE)
EXPECTED_VERSES = 6236


def build_inventory() -> dict:
    mapped: dict[str, str] = {}
    unmatched: list[str] = []
    duplicates: dict[str, list[str]] = {}
    with RemoteZip(ARCHIVE_URL) as archive:
        for name in archive.namelist():
            match = ENTRY_RE.search(name)
            if not match:
                continue
            surah, ayah = map(int, match.groups())
            if not (1 <= surah <= 114 and 1 <= ayah <= 286):
                unmatched.append(name)
                continue
            key = f"{surah}:{ayah}"
            if key in mapped:
                duplicates.setdefault(key, [mapped[key]]).append(name)
            else:
                mapped[key] = name

    missing = []
    # Validate the archive inventory against canonical surah verse counts.
    counts = [7,286,200,176,120,165,206,75,129,109,123,111,43,52,99,128,111,110,98,135,112,78,118,64,77,227,93,88,69,60,34,30,73,54,45,83,182,88,75,85,54,53,89,59,37,35,38,29,18,45,60,49,62,55,78,96,29,22,24,13,14,11,11,18,12,12,30,52,52,44,28,28,20,56,40,31,50,40,46,42,29,19,36,25,22,17,19,26,30,20,15,21,11,8,8,19,5,8,8,11,11,8,3,9,5,4,7,3,6,3,5,4,5,6]
    if len(counts) != 114:
        raise RuntimeError("Internal surah verse-count table is invalid.")
    for surah, count in enumerate(counts, 1):
        for ayah in range(1, count + 1):
            key = f"{surah}:{ayah}"
            if key not in mapped:
                missing.append(key)

    if duplicates or missing or len(mapped) != EXPECTED_VERSES:
        raise SystemExit(
            "Official archive inventory did not validate: "
            f"mapped={len(mapped)}, missing={len(missing)}, "
            f"duplicates={len(duplicates)}. Refusing incomplete catalog."
        )
    return {
        "source_url": ARCHIVE_URL,
        "recitation": "Hafs",
        "reciter_internal": "Maher Al-Muaiqly",
        "mapping_status": "archive_entries_enumerated_requires_audio_and_rights_review",
        "expected_verse_count": EXPECTED_VERSES,
        "mapped_verse_count": len(mapped),
        "verses": dict(sorted(mapped.items(), key=lambda item: tuple(map(int, item[0].split(":"))))),
    }


if __name__ == "__main__":
    destination = Path(sys.argv[1] if len(sys.argv) > 1 else "output/official_verse_audio_inventory.json")
    destination.parent.mkdir(parents=True, exist_ok=True)
    inventory = build_inventory()
    destination.write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Validated archive mapping for {inventory['mapped_verse_count']} verses: {destination}")
