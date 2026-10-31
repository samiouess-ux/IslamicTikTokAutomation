"""Generate draft Quran manifests from the multi-surah batch and audio report.

Drafts are deliberately NOT renderable: exact recitation, reuse rights,
Arabic/translation review, and an approved background remain mandatory.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def build_draft_manifests(batch: dict[str, Any], report: dict[str, Any], output_dir: Path) -> list[dict]:
    if batch.get("batch_status") != "review_candidates_only":
        raise ValueError("Only review candidate batches are accepted.")
    if report.get("rendering_allowed") is not False or report.get("auto_publish") is not False:
        raise ValueError("Audio report must remain review-only.")
    passages = {item["candidate_id"]: item for item in batch.get("passages", [])}
    output_dir.mkdir(parents=True, exist_ok=True)
    created = []
    for audio_item in report.get("items", []):
        if not audio_item.get("status", "").startswith("audio_prepared"):
            continue
        candidate = passages.get(audio_item["candidate_id"])
        if not candidate:
            raise ValueError(f"Audio candidate missing from batch: {audio_item['candidate_id']}")
        if int(candidate["surah_number"]) != int(audio_item["surah_number"]):
            raise ValueError("Surah mismatch between batch and audio report.")
        expected = [int(v["ayah"]) for v in candidate["verses"]]
        if audio_item.get("selected_verses") != expected:
            raise ValueError("Prepared audio does not contain every requested ayah in order.")
        if not audio_item.get("audio_file"):
            raise ValueError("Prepared audio file path is missing.")
        verses = [{
            "number": int(v["ayah"]),
            "arabic": v["arabic_uthmani"].lstrip("\ufeff"),
            "english": v["english_saheeh_international"],
        } for v in candidate["verses"]]
        surah = int(candidate["surah_number"])
        from render_quran_review_previews import SURAH_NAMES
        if not 1 <= surah <= len(SURAH_NAMES):
            raise ValueError(f"Invalid Quran surah number: {surah}")
        surah_name_ar = SURAH_NAMES[surah - 1]
        manifest = {
            "id": candidate["candidate_id"],
            "content_type": "quran",
            "status": "draft_candidate_requires_human_review",
            "rotation_approved": False,
            "source": {
                "surah_number": surah,
                "surah_name_ar": surah_name_ar,
                "verses": expected,
                "references": [v["reference"] for v in candidate["verses"]],
                "arabic_source": "Quran Uthmani joined candidate catalog; not yet human-reviewed",
                "translation_name": "Saheeh International",
                "translation_rights_confirmed": False,
            },
            "verses": verses,
            "audio": {
                "required": True,
                "kind": "quran_recitation",
                "production_audio_file": audio_item["audio_file"],
                "processed_verse_durations_seconds": {str(k): v for k, v in audio_item["verse_durations_seconds"].items()},
                "inter_verse_silence_seconds": 0.0,
                "approved": False,
                "preview_only": False,
                "exact_recording_user_reviewed": False,
                "rights_verified": False,
                "music_allowed": False,
                "notes": "Official archive files concatenated whole, in ayah order, without trimming or time-stretching. Listen to this exact file and verify reuse rights before rendering.",
            },
            "visual": {
                "format": "9:16",
                "width": 1080,
                "height": 1920,
                "fps": 30,
                "template": "ornate_gold_classic",
                "template_approved": True,
                "background_style": "awaiting approved background",
                "background_candidate": {},
            },
            "publishing": {
                "approval_required": True,
                "auto_publish": False,
                "telegram_delivery": False,
                "manual_review_required": True,
            },
            "caption": {
                "text": f"سورة {surah_name_ar} | الآيات {expected[0]}-{expected[-1]}",
                "references": [v["reference"] for v in candidate["verses"]],
            },
            "preflight": {
                "audio_duration_seconds": audio_item["duration_seconds"],
                "audio_approved": False,
                "rendering_allowed": False,
                "telegram_delivery": False,
                "auto_publish": False,
                "blockers": [
                    "human verification of exact Arabic text",
                    "translation reuse rights confirmation",
                    "listen to and approve the exact recitation",
                    "document recording reuse permission",
                    "select and explicitly approve a licensed background",
                ],
            },
        }
        path = output_dir / f"{candidate['candidate_id']}.json"
        if path.exists():
            raise ValueError(f"Refusing to overwrite draft manifest: {path}")
        path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        created.append({"candidate_id": candidate["candidate_id"], "surah_number": surah, "manifest": str(path), "rendering_allowed": False})
    if len(created) < 2:
        raise ValueError("At least two distinct-surah audio drafts are required.")
    if len({item["surah_number"] for item in created}) != len(created):
        raise ValueError("Draft manifests must represent distinct surahs.")
    return created


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", type=Path, required=True)
    parser.add_argument("--audio-report", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("output/quran_draft_manifests"))
    parser.add_argument("--report", type=Path, default=Path("output/quran_draft_manifest_report.json"))
    args = parser.parse_args()
    result = build_draft_manifests(
        json.loads(args.batch.read_text(encoding="utf-8")),
        json.loads(args.audio_report.read_text(encoding="utf-8")),
        args.output_dir,
    )
    summary = {
        "status": "draft_manifests_generated_for_review",
        "manifest_count": len(result),
        "distinct_surah_count": len({x["surah_number"] for x in result}),
        "items": result,
        "rendering_allowed": False,
        "telegram_delivery": False,
        "auto_publish": False,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
