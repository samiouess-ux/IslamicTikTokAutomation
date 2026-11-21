"""Fail-closed reservation ledger for Telegram Quran video delivery.

A reservation is committed to the active Git branch before calling Telegram.
If the outcome is ambiguous, the pending file remains and later sends are blocked.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def delivery_duration_limit_seconds(selected_verses: list[int]) -> float:
    """Return the hard delivery ceiling: 60 seconds for any complete-ayah part."""
    if not isinstance(selected_verses, list) or not selected_verses:
        raise ValueError("Delivery duration requires at least one selected ayah.")
    return 60.0


def guard_no_pending(pending_path: Path) -> None:
    if pending_path.exists():
        pending = _read_json(pending_path, {})
        candidate_id = pending.get("candidate_id", "unknown") if isinstance(pending, dict) else "unknown"
        raise RuntimeError(
            f"Unresolved Telegram delivery attempt for {candidate_id}; refusing another automatic send."
        )


def reserve_attempt(
    pending_path: Path,
    history_path: Path,
    batch_path: Path,
    audio_report_path: Path,
    preview_report_path: Path,
) -> dict:
    guard_no_pending(pending_path)
    history = _read_json(history_path, {"schema_version": 1, "ayah_references": [], "deliveries": []})
    if history.get("schema_version") != 1 or not isinstance(history.get("ayah_references"), list):
        raise ValueError("Quran delivery history is malformed or unsupported.")

    batch = _read_json(batch_path, {})
    audio_report = _read_json(audio_report_path, {})
    preview_report = _read_json(preview_report_path, {})
    items = preview_report.get("items", [])
    if preview_report.get("preview_count") != 1 or preview_report.get("auto_publish") is not False or len(items) != 1:
        raise ValueError("Reservation requires exactly one review-only preview and disabled auto-publishing.")

    candidate_id = items[0].get("candidate_id")
    preview_item = items[0]
    if preview_item.get("review_only") is not True:
        raise ValueError("Reservation requires a review-only preview.")
    preview_duration = preview_item.get("duration_seconds")
    audio_items = [p for p in audio_report.get("items", []) if p.get("candidate_id") == candidate_id]
    if len(audio_items) != 1:
        raise ValueError("Could not match exactly one preview and audio report item.")
    audio_item = audio_items[0]
    source_candidate_id = audio_item.get("source_candidate_id", candidate_id)
    if preview_item.get("source_candidate_id", source_candidate_id) != source_candidate_id:
        raise ValueError("Preview source candidate does not match its audio report.")
    passages = [p for p in batch.get("passages", []) if p.get("candidate_id") == source_candidate_id]
    if len(passages) != 1:
        raise ValueError("Could not match exactly one source passage for the selected audio part.")
    passage = passages[0]
    if not str(audio_item.get("status", "")).startswith("audio_prepared"):
        raise ValueError("Cannot reserve a passage without prepared audio.")
    audio_duration = audio_item.get("duration_seconds")

    source_verses = passage.get("verses", [])
    selected = audio_item.get("selected_verses")
    if (
        not isinstance(selected, list) or not selected
        or any(isinstance(n, bool) or not isinstance(n, int) for n in selected)
        or selected != [int(v["ayah"]) for v in source_verses[:len(selected)]]
        or selected != list(range(selected[0], selected[0] + len(selected)))
    ):
        raise ValueError("Reserved ayahs must be a non-empty contiguous prefix of the source passage.")
    allowed_seconds = delivery_duration_limit_seconds(selected)
    if not isinstance(preview_duration, (int, float)) or preview_duration <= 0 or preview_duration > allowed_seconds:
        raise ValueError(f"Preview duration must be positive and no longer than {allowed_seconds:g} seconds.")
    if not isinstance(audio_duration, (int, float)) or audio_duration <= 0 or audio_duration > allowed_seconds:
        raise ValueError(f"Prepared audio duration must be positive and no longer than {allowed_seconds:g} seconds.")
    refs = [str(v.get("reference", "")) for v in source_verses[:len(selected)]]
    if len(refs) != len(selected) or any(not ref or ":" not in ref for ref in refs):
        raise ValueError("Every reserved ayah must have an exact surah:ayah reference.")
    if set(refs).intersection(history["ayah_references"]):
        raise ValueError("Refusing to reserve ayahs already present in confirmed delivery history.")

    pending = {
        "schema_version": 1,
        "status": "sending_or_outcome_unknown",
        "candidate_id": candidate_id,
        "source_candidate_id": source_candidate_id,
        "surah_number": passage.get("surah_number"),
        "selected_verses": selected,
        "ayah_references": refs,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "recovery_note": "Do not resend automatically. Reconcile against the Telegram chat before clearing this reservation.",
    }
    _write_json(pending_path, pending)
    return pending


def finalize_attempt(
    pending_path: Path,
    history_path: Path,
    batch_path: Path,
    audio_report_path: Path,
    candidate_id: str,
) -> dict:
    pending = _read_json(pending_path)
    if not isinstance(pending, dict) or pending.get("candidate_id") != candidate_id:
        raise RuntimeError("No matching pending Telegram reservation; refusing to record delivery.")
    history = _read_json(history_path, {"schema_version": 1, "ayah_references": [], "deliveries": []})
    batch = _read_json(batch_path, {})
    audio_report = _read_json(audio_report_path, {})
    audio_items = [p for p in audio_report.get("items", []) if p.get("candidate_id") == candidate_id]
    if len(audio_items) != 1:
        raise ValueError("Could not identify exactly one reserved audio report item.")
    audio_item = audio_items[0]
    source_candidate_id = audio_item.get("source_candidate_id", candidate_id)
    if pending.get("source_candidate_id", source_candidate_id) != source_candidate_id:
        raise ValueError("Pending reservation source candidate no longer matches the audio report.")
    passages = [p for p in batch.get("passages", []) if p.get("candidate_id") == source_candidate_id]
    if len(passages) != 1:
        raise ValueError("Could not identify exactly one source passage for the reserved audio.")
    if pending.get("selected_verses") != audio_item.get("selected_verses"):
        raise ValueError("Pending reservation ayahs no longer match the selected audio ayahs.")
    if pending.get("ayah_references") != [
        str(v.get("reference", "")) for v in passages[0].get("verses", [])[:len(pending.get("selected_verses", []))]
    ]:
        raise ValueError("Pending reservation no longer matches the source candidate.")
    from record_quran_delivery import record_delivery, save_history
    record_delivery(history, passages[0], pending["selected_verses"])
    save_history(history, history_path)
    pending_path.unlink()
    return history


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    guard = sub.add_parser("guard")
    guard.add_argument("--pending", type=Path, required=True)
    reserve = sub.add_parser("reserve")
    reserve.add_argument("--pending", type=Path, required=True)
    reserve.add_argument("--history", type=Path, required=True)
    reserve.add_argument("--batch", type=Path, required=True)
    reserve.add_argument("--audio-report", type=Path, required=True)
    reserve.add_argument("--preview-report", type=Path, required=True)
    finalize = sub.add_parser("finalize")
    finalize.add_argument("--pending", type=Path, required=True)
    finalize.add_argument("--history", type=Path, required=True)
    finalize.add_argument("--batch", type=Path, required=True)
    finalize.add_argument("--audio-report", type=Path, required=True)
    finalize.add_argument("--candidate-id", required=True)
    args = parser.parse_args()

    if args.command == "guard":
        guard_no_pending(args.pending)
    elif args.command == "reserve":
        attempt = reserve_attempt(args.pending, args.history, args.batch, args.audio_report, args.preview_report)
        print(f"Reserved {attempt['candidate_id']} ({len(attempt['ayah_references'])} ayahs) before Telegram send.")
    else:
        history = finalize_attempt(args.pending, args.history, args.batch, args.audio_report, args.candidate_id)
        print(f"Confirmed Telegram delivery recorded; {len(history['ayah_references'])} total ayahs protected from reuse.")


if __name__ == "__main__":
    main()
