"""Fetch and validate the complete Quran translation from QuranEnc.

The downloader fails closed unless the published English Saheeh translation
entry is present and every one of the 6,236 ayahs has an exact non-empty
translation. It preserves source wording verbatim and records provenance.
"""
from __future__ import annotations

import argparse
import json
import urllib.request
from pathlib import Path

BASE = "https://quranenc.com/api/v1"
TRANSLATION_KEY = "english_saheeh"
COUNTS = [7,286,200,176,120,165,206,75,129,109,123,111,43,52,99,128,111,110,98,135,112,78,118,64,77,227,93,88,69,60,34,30,73,54,45,83,182,88,75,85,54,53,89,59,37,35,38,29,18,45,60,49,62,55,78,96,29,22,24,13,14,11,11,18,12,12,30,52,52,44,28,28,20,56,40,31,50,40,46,42,29,19,36,25,22,17,19,26,30,20,15,21,11,8,8,19,5,8,8,11,11,8,3,9,5,4,7,3,6,3,5,4,5,6]


def fetch_json(url: str):
    request = urllib.request.Request(url, headers={"User-Agent": "IslamicTikTokAutomation/1.0"})
    with urllib.request.urlopen(request, timeout=45) as response:
        return json.loads(response.read().decode("utf-8"))


def find_translation_metadata(items: list[dict]) -> dict:
    matches = [item for item in items if item.get("key") == TRANSLATION_KEY]
    if len(matches) != 1:
        raise ValueError(
            f"Expected exactly one {TRANSLATION_KEY} translation entry, found {len(matches)}"
        )
    metadata = matches[0]
    title = str(metadata.get("title", "")).lower()
    if "saheeh" not in title and "sahih" not in title:
        raise ValueError(f"Translation title does not identify Saheeh/Sahih: {metadata.get('title')!r}")
    if not metadata.get("version"):
        raise ValueError("Translation API did not provide a version identifier")
    return metadata


def build_catalog(fetcher=fetch_json) -> dict:
    if len(COUNTS) != 114 or sum(COUNTS) != 6236:
        raise ValueError("Internal canonical verse-count table is invalid")
    metadata_payload = fetcher(f"{BASE}/translations/list/en?localization=en")
    if not isinstance(metadata_payload, list):
        raise ValueError("Translation list API response is not a JSON array")
    metadata = find_translation_metadata(metadata_payload)

    verses: dict[str, str] = {}
    for surah, expected_count in enumerate(COUNTS, 1):
        payload = fetcher(f"{BASE}/translation/sura/{TRANSLATION_KEY}/{surah}")
        if not isinstance(payload, list):
            raise ValueError(f"Surah {surah}: translation API response is not an array")
        seen = set()
        for item in payload:
            if not isinstance(item, dict):
                raise ValueError(f"Surah {surah}: malformed translation item")
            if item.get("sura") != surah:
                raise ValueError(f"Surah {surah}: API returned a mismatched surah number")
            ayah = item.get("aya")
            text = item.get("translation")
            if not isinstance(ayah, int) or not 1 <= ayah <= expected_count:
                raise ValueError(f"Surah {surah}: invalid ayah number {ayah!r}")
            if ayah in seen or not isinstance(text, str) or not text.strip():
                raise ValueError(f"Surah {surah}:{ayah}: duplicate or empty translation")
            seen.add(ayah)
            verses[f"{surah}:{ayah}"] = text
        if seen != set(range(1, expected_count + 1)):
            missing = sorted(set(range(1, expected_count + 1)) - seen)
            raise ValueError(f"Surah {surah}: incomplete translation, missing {missing[:10]}")

    if len(verses) != 6236:
        raise ValueError(f"Expected 6,236 translations, received {len(verses)}")
    return {
        "source": "QuranEnc.com API",
        "source_url": "https://quranenc.com/en/home/api/",
        "translation_key": TRANSLATION_KEY,
        "translation_title": metadata["title"],
        "version": metadata["version"],
        "last_update": metadata.get("last_update"),
        "language": "en",
        "terms": [
            "Do not modify, add to, or delete translation content.",
            "Attribute QuranEnc.com as publisher and source.",
            "Include the translation version and transcript information.",
            "Keep this corpus updated to the latest issued version.",
        ],
        "status": "complete_source_corpus_requires_verse_level_review_before_publication",
        "expected_verse_count": 6236,
        "translated_verse_count": len(verses),
        "verses": dict(sorted(verses.items(), key=lambda pair: tuple(map(int, pair[0].split(":"))))),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("output/english_saheeh_translation.json"))
    args = parser.parse_args()
    catalog = build_catalog()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Validated {catalog['translated_verse_count']} translations from {catalog['translation_title']} ({catalog['version']})")


if __name__ == "__main__":
    main()
