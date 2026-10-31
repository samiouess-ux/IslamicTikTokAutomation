"""Create a diverse, review-only Quran passage batch from the full joined corpus.

This stage selects complete contiguous ayah ranges from different surahs and
carries exact source strings/audio archive members forward. It does NOT approve
religious text, translations, recordings, backgrounds, or publication.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def _ordered_surahs(joined: dict[str, Any]) -> list[int]:
    keys = joined.get("verses")
    if not isinstance(keys, dict):
        raise ValueError("Joined catalog must contain a verses object.")
    surahs = sorted({int(key.split(":")[0]) for key in keys}, key=int)
    if not surahs or any(not 1 <= number <= 114 for number in surahs):
        raise ValueError("Joined catalog has no valid Quran surah keys.")
    return surahs


def build_review_batch(
    joined: dict[str, Any],
    count: int = 5,
    verses_per_passage: int = 3,
    seed: str = "quran-review-batch",
) -> dict[str, Any]:
    if joined.get("rendering_allowed") is not False:
        raise ValueError("Input catalog must remain blocked from rendering.")
    if joined.get("status") != "complete_join_candidate_requires_human_review_and_recording_approval":
        raise ValueError("Input must be the complete joined review candidate catalog.")
    if count < 1 or verses_per_passage < 1:
        raise ValueError("count and verses_per_passage must be positive.")
    corpus = joined.get("verses")
    if not isinstance(corpus, dict) or len(corpus) != joined.get("expected_verse_count"):
        raise ValueError("Joined corpus is incomplete or its verse count does not match.")
    surahs = _ordered_surahs(joined)
    if count > len(surahs):
        raise ValueError(f"Cannot select {count} distinct surahs from {len(surahs)} available.")

    # Spread choices across the Quran instead of repeatedly selecting one short
    # opening passage. A stable hash makes the same seed reproducible.
    digest = hashlib.sha256(seed.encode("utf-8")).digest()
    offset = int.from_bytes(digest[:8], "big") % len(surahs)
    ordered = surahs[offset:] + surahs[:offset]
    slots = sorted({min(len(ordered)-1, (i * len(ordered)) // count) for i in range(count)})
    selected_surahs = [ordered[i] for i in slots]
    passages = []

    for index, surah in enumerate(selected_surahs, start=1):
        available = sorted(
            int(key.split(":")[1])
            for key in corpus
            if int(key.split(":")[0]) == surah
        )
        if len(available) < verses_per_passage:
            raise ValueError(f"Surah {surah} has fewer than {verses_per_passage} catalogued verses.")
        # Select a deterministic contiguous window while preserving ayah order.
        max_start = len(available) - verses_per_passage
        local_digest = hashlib.sha256(f"{seed}:{surah}".encode("utf-8")).digest()
        start_index = int.from_bytes(local_digest[:4], "big") % (max_start + 1)
        numbers = available[start_index:start_index + verses_per_passage]
        if numbers != list(range(numbers[0], numbers[0] + verses_per_passage)):
            raise ValueError(f"Surah {surah} has a non-contiguous verse catalog window.")
        verses = []
        for number in numbers:
            key = f"{surah}:{number}"
            row = corpus.get(key)
            if not isinstance(row, dict):
                raise ValueError(f"Missing joined verse record: {key}")
            arabic = row.get("arabic_uthmani")
            english = row.get("english_saheeh_international")
            audio_member = row.get("audio_archive_member")
            if not all(isinstance(v, str) and v.strip() for v in (arabic, english, audio_member)):
                raise ValueError(f"Incomplete Arabic/translation/audio mapping for {key}.")
            verses.append({
                "ayah": number,
                "reference": key,
                "arabic_uthmani": arabic,
                "english_saheeh_international": english,
                "official_audio_archive_member": audio_member,
            })
        passages.append({
            "candidate_id": f"quran_s{surah:03d}_{numbers[0]:03d}_{numbers[-1]:03d}",
            "surah_number": surah,
            "verse_numbers": numbers,
            "verses": verses,
            "status": "candidate_requires_human_review",
            "approval": {
                "arabic_text_reviewed": False,
                "translation_rights_confirmed": False,
                "exact_recitation_listened_to": False,
                "recording_reuse_approved": False,
                "background_licensed_and_user_approved": False,
                "ready_to_render": False,
                "ready_to_publish": False,
            },
        })

    if len({item["surah_number"] for item in passages}) != count:
        raise ValueError("Batch must contain distinct surahs.")
    return {
        "schema_version": 1,
        "batch_status": "review_candidates_only",
        "seed": seed,
        "candidate_count": len(passages),
        "distinct_surah_count": len({item["surah_number"] for item in passages}),
        "verses_per_passage": verses_per_passage,
        "source_catalog_status": joined["status"],
        "rendering_allowed": False,
        "auto_publish": False,
        "telegram_delivery": False,
        "note": "These are diverse source candidates, not approved videos. Exact Quran wording, translation reuse rights, recording, and visual asset must pass review before rendering.",
        "passages": passages,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a multi-surah Quran review candidate batch.")
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("output/quran_review_batch.json"))
    parser.add_argument("--count", type=int, default=5)
    parser.add_argument("--verses-per-passage", type=int, default=3)
    parser.add_argument("--seed", default="quran-review-batch")
    args = parser.parse_args()
    joined = json.loads(args.catalog.read_text(encoding="utf-8"))
    result = build_review_batch(joined, args.count, args.verses_per_passage, args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Built {result['candidate_count']} review-only passages from {result['distinct_surah_count']} different surahs; no approvals or delivery were triggered.")


if __name__ == "__main__":
    main()
