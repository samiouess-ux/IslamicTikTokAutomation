"""Record only the exact ayahs included in a Telegram-confirmed Quran video."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

EMPTY = {"schema_version": 1, "ayah_references": [], "deliveries": []}


def record_delivery(history: dict, passage: dict, selected_verses: list[int]) -> dict:
    if (
        history.get("schema_version") != 1
        or not isinstance(history.get("ayah_references"), list)
        or not isinstance(history.get("deliveries"), list)
    ):
        raise ValueError("Unsupported or malformed Quran delivery history.")

    source_verses = passage.get("verses", [])
    if not isinstance(source_verses, list) or not source_verses:
        raise ValueError("Source candidate must contain ayahs.")
    source_numbers = [int(v["ayah"]) for v in source_verses]
    if (
        not isinstance(selected_verses, list)
        or not selected_verses
        or any(isinstance(n, bool) or not isinstance(n, int) for n in selected_verses)
        or selected_verses != source_numbers[:len(selected_verses)]
        or selected_verses != list(range(selected_verses[0], selected_verses[0] + len(selected_verses)))
    ):
        raise ValueError("Delivered ayahs must be a non-empty contiguous prefix of the source candidate.")

    selected_set = set(selected_verses)
    refs = [
        str(v.get("reference", ""))
        for v in source_verses
        if int(v["ayah"]) in selected_set
    ]
    if len(refs) != len(selected_verses) or any(not ref or ":" not in ref for ref in refs):
        raise ValueError("Every delivered ayah must have an exact surah:ayah reference.")
    if set(refs).intersection(history["ayah_references"]):
        raise ValueError("Refusing to record a passage containing previously delivered ayahs.")

    history["ayah_references"].extend(refs)
    history["deliveries"].append({
        "candidate_id": passage.get("candidate_id"),
        "surah_number": passage.get("surah_number"),
        "selected_verses": selected_verses,
        "ayah_references": refs,
        "delivered_at_utc": datetime.now(timezone.utc).isoformat(),
    })
    return history


def save_history(history: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(history, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--history", type=Path, required=True)
    parser.add_argument("--batch", type=Path, required=True)
    parser.add_argument("--audio-report", type=Path, required=True)
    parser.add_argument("--candidate-id", required=True)
    args = parser.parse_args()

    history = json.loads(args.history.read_text(encoding="utf-8")) if args.history.exists() else dict(EMPTY)
    batch = json.loads(args.batch.read_text(encoding="utf-8"))
    report = json.loads(args.audio_report.read_text(encoding="utf-8"))
    matches = [p for p in batch.get("passages", []) if p.get("candidate_id") == args.candidate_id]
    audio_matches = [item for item in report.get("items", []) if item.get("candidate_id") == args.candidate_id]
    if len(matches) != 1 or len(audio_matches) != 1:
        raise SystemExit("Could not identify exactly one delivered candidate and audio report item.")
    audio_item = audio_matches[0]
    if not str(audio_item.get("status", "")).startswith("audio_prepared"):
        raise SystemExit("Cannot record delivery without a prepared audio passage.")
    selected = audio_item.get("selected_verses")
    record_delivery(history, matches[0], selected)
    save_history(history, args.history)
    print(f"Recorded {len(selected)} actually delivered ayahs in persistent history.")


if __name__ == "__main__":
    main()
