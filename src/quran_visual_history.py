"""Persistent anti-repetition history for delivered Quran video visuals."""
from __future__ import annotations
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

EMPTY = {"schema_version": 1, "deliveries": []}
BACKGROUND_WINDOW = 6
COVER_WINDOW = 3


def load_history(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"schema_version": 1, "deliveries": []}
    history = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(history, dict) or history.get("schema_version") != 1 or not isinstance(history.get("deliveries"), list):
        raise ValueError("Visual history is malformed or unsupported.")
    for delivery in history["deliveries"]:
        if not isinstance(delivery, dict) or not isinstance(delivery.get("candidate_id"), str) or not isinstance(delivery.get("backgrounds"), list):
            raise ValueError("Visual history contains a malformed delivery.")
    return history


def recent_usage(history: dict[str, Any], background_window: int = BACKGROUND_WINDOW,
                 cover_window: int = COVER_WINDOW) -> tuple[set[str], set[str], set[str]]:
    if history.get("schema_version") != 1 or not isinstance(history.get("deliveries"), list):
        raise ValueError("Visual history is malformed or unsupported.")
    recent = history["deliveries"][-background_window:] if background_window else []
    background_ids, categories = set(), set()
    for delivery in recent:
        for background in delivery.get("backgrounds", []):
            asset_id = background.get("id")
            if isinstance(asset_id, str) and asset_id:
                background_ids.add(asset_id)
            for category in background.get("categories", []):
                if isinstance(category, str) and category:
                    categories.add(category.lower())
    covers = history["deliveries"][-cover_window:] if cover_window else []
    cover_ids = {item["cover_template_id"] for item in covers
                 if isinstance(item.get("cover_template_id"), str) and item["cover_template_id"]}
    return background_ids, categories, cover_ids


def record_visual_delivery(history: dict[str, Any], report: dict[str, Any],
                           telegram_confirmed: bool = False) -> dict[str, Any]:
    if not telegram_confirmed:
        raise ValueError("Visual history can only be recorded after confirmed Telegram delivery.")
    if history.get("schema_version") != 1 or not isinstance(history.get("deliveries"), list):
        raise ValueError("Visual history is malformed or unsupported.")
    items = report.get("items")
    if report.get("preview_count") != 1 or not isinstance(items, list) or len(items) != 1:
        raise ValueError("Expected exactly one Telegram-confirmed review video.")
    item = items[0]
    candidate_id, cover_id, sequence = item.get("candidate_id"), item.get("cover_template_id"), item.get("background_sequence")
    if not isinstance(candidate_id, str) or not candidate_id.strip():
        raise ValueError("A stable candidate id is required.")
    if not isinstance(cover_id, str) or not cover_id.strip():
        raise ValueError("A selected cover template id is required.")
    if not isinstance(sequence, list) or not sequence:
        raise ValueError("The delivered video must include at least one background.")
    backgrounds = []
    for background in sequence:
        asset_id = background.get("id")
        if not isinstance(asset_id, str) or not asset_id.strip():
            raise ValueError("Every delivered background must have a stable id.")
        tags = background.get("tags", [])
        if not isinstance(tags, list):
            tags = []
        backgrounds.append({
            "id": asset_id,
            "categories": sorted({str(tag).strip().lower() for tag in tags if isinstance(tag, str) and tag.strip()}),
            "background_type": background.get("background_type", "unknown"),
        })
    entry = {"candidate_id": candidate_id, "backgrounds": backgrounds, "cover_template_id": cover_id}
    existing = next((x for x in history["deliveries"] if x.get("candidate_id") == candidate_id), None)
    if existing:
        if {key: existing.get(key) for key in entry} != entry:
            raise ValueError("Candidate id already exists with different visual assets; refusing overwrite.")
        return history
    history["deliveries"].append({**entry, "confirmed_at_utc": datetime.now(timezone.utc).isoformat()})
    return history


def save_history(history: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(history, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["record"])
    parser.add_argument("--history", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--telegram-confirmed", action="store_true",
                        help="Required gate; invoke only inside a successful Telegram-send step.")
    args = parser.parse_args()
    if not args.telegram_confirmed:
        raise SystemExit("Refusing to record visuals without confirmed Telegram delivery.")
    history = load_history(args.history)
    report = json.loads(args.report.read_text(encoding="utf-8"))
    record_visual_delivery(history, report, telegram_confirmed=True)
    save_history(history, args.history)
    print(f"Recorded delivered visual assets for {report['items'][0]['candidate_id']}.")


if __name__ == "__main__":
    main()
