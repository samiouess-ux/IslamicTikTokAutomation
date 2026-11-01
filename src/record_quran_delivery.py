"""Record only Quran passages whose Telegram send was confirmed successful."""
from __future__ import annotations
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

EMPTY = {"schema_version": 1, "ayah_references": [], "deliveries": []}

def record_delivery(history: dict, passage: dict) -> dict:
    if history.get("schema_version") != 1 or not isinstance(history.get("ayah_references"), list) or not isinstance(history.get("deliveries"), list):
        raise ValueError("Unsupported or malformed Quran delivery history.")
    refs = [str(v.get("reference", "")) for v in passage.get("verses", [])]
    if not refs or any(not ref or ":" not in ref for ref in refs):
        raise ValueError("Delivered passage must contain exact surah:ayah references.")
    if set(refs).intersection(history["ayah_references"]):
        raise ValueError("Refusing to record a passage containing previously delivered ayahs.")
    history["ayah_references"].extend(refs)
    history["deliveries"].append({"candidate_id": passage.get("candidate_id"), "surah_number": passage.get("surah_number"), "ayah_references": refs, "delivered_at_utc": datetime.now(timezone.utc).isoformat()})
    return history

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--history", type=Path, required=True)
    parser.add_argument("--batch", type=Path, required=True)
    parser.add_argument("--candidate-id", required=True)
    args = parser.parse_args()
    history = json.loads(args.history.read_text(encoding="utf-8")) if args.history.exists() else dict(EMPTY)
    batch = json.loads(args.batch.read_text(encoding="utf-8"))
    matches = [p for p in batch.get("passages", []) if p.get("candidate_id") == args.candidate_id]
    if len(matches) != 1:
        raise SystemExit("Could not identify exactly one delivered candidate in the batch.")
    record_delivery(history, matches[0])
    args.history.parent.mkdir(parents=True, exist_ok=True)
    args.history.write_text(json.dumps(history, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
    print(f"Recorded {len(matches[0]['verses'])} delivered ayahs in persistent history.")

if __name__ == "__main__":
    main()
