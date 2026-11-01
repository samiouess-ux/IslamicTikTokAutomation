"""Persistent, bounded Telegram update deduplication state (JSON file)."""
from __future__ import annotations

import json
from pathlib import Path

MAX_PROCESSED_UPDATE_IDS = 5000


def load_state(path: Path) -> dict:
    """Load state; missing file starts clean, malformed state fails closed."""
    path = Path(path)
    if not path.exists():
        return {"schema_version": 1, "last_update_id": 0, "processed_update_ids": []}
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("Telegram inbox state is unreadable; refusing to continue.") from exc
    if not isinstance(state, dict) or state.get("schema_version") != 1:
        raise ValueError("Unsupported Telegram inbox state schema.")
    last_id = state.get("last_update_id")
    processed = state.get("processed_update_ids")
    if not isinstance(last_id, int) or last_id < 0 or not isinstance(processed, list):
        raise ValueError("Telegram inbox state has invalid fields.")
    if any(not isinstance(item, int) or item < 0 for item in processed):
        raise ValueError("Telegram inbox state contains invalid update IDs.")
    return {"schema_version": 1, "last_update_id": last_id,
            "processed_update_ids": list(dict.fromkeys(processed))[-MAX_PROCESSED_UPDATE_IDS:]}


def is_duplicate(state: dict, update_id: int) -> bool:
    """Return true if this Telegram update has already been recorded."""
    if not isinstance(update_id, int) or update_id < 0:
        raise ValueError("Telegram update_id must be a non-negative integer.")
    return update_id <= state["last_update_id"] or update_id in state["processed_update_ids"]


def record_update(state: dict, update_id: int) -> dict:
    """Return a new state with update recorded; caller must persist it atomically."""
    if is_duplicate(state, update_id):
        return dict(state)
    processed = (state["processed_update_ids"] + [update_id])[-MAX_PROCESSED_UPDATE_IDS:]
    return {"schema_version": 1, "last_update_id": max(state["last_update_id"], update_id),
            "processed_update_ids": processed}


def save_state(state: dict, path: Path) -> None:
    """Write state via temp file + atomic replace to avoid partial JSON."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)
