"""Durable local ledger primitives for Pro content delivery idempotency.

The workflow must persist this ledger after every state transition. A reserved
or uncertain manifest is never eligible for another send until reconciled.
"""
from __future__ import annotations

import argparse
import json
import os
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

VALID_STATES = {"reserved", "delivered", "uncertain"}


def _require_manifest_id(manifest_id: str) -> None:
    if not isinstance(manifest_id, str) or not manifest_id.strip():
        raise ValueError("A non-empty manifest_id is required.")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def _file_lock(path: Path) -> Iterator[None]:
    """Serialize read/modify/write operations between processes on one runner."""
    lock_path = path.with_name(path.name + ".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+b") as stream:
        if os.name == "nt":
            import msvcrt
            stream.seek(0)
            if stream.tell() == 0:
                stream.write(b"0")
                stream.flush()
            stream.seek(0)
            msvcrt.locking(stream.fileno(), msvcrt.LK_LOCK, 1)
            try:
                yield
            finally:
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def load_ledger(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"version": 1, "entries": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot read Pro reservation ledger: {exc}") from exc
    if not isinstance(data, dict) or type(data.get("version")) is not int or data.get("version") != 1 or not isinstance(data.get("entries"), dict):
        raise ValueError("Invalid Pro reservation ledger structure.")
    for key, entry in data["entries"].items():
        if (
            not isinstance(key, str) or not key.strip()
            or not isinstance(entry, dict)
            or not isinstance(entry.get("content_type"), str)
            or entry.get("content_type") not in {"dua", "dhikr"}
            or not isinstance(entry.get("state"), str)
            or entry.get("state") not in VALID_STATES
            or not isinstance(entry.get("run_id"), str)
            or not entry.get("run_id", "").strip()
            or not isinstance(entry.get("created_at"), str)
            or not entry.get("created_at", "").strip()
            or not isinstance(entry.get("updated_at"), str)
            or not entry.get("updated_at", "").strip()
        ):
            raise ValueError("Invalid Pro reservation ledger entry.")
        message_id = entry.get("telegram_message_id")
        if entry["state"] == "delivered":
            if isinstance(message_id, bool) or not isinstance(message_id, int) or message_id <= 0:
                raise ValueError("Invalid Pro reservation ledger entry.")
        elif message_id is not None:
            raise ValueError("Invalid Pro reservation ledger entry.")
    return data


def save_ledger(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def reserve(path: Path, manifest_id: str, content_type: str, run_id: str) -> dict[str, Any]:
    if not isinstance(content_type, str) or content_type not in {"dua", "dhikr"}:
        raise ValueError("Only dua/dhikr can be reserved by Pro.")
    if not isinstance(manifest_id, str) or not manifest_id.strip() or not isinstance(run_id, str) or not run_id.strip():
        raise ValueError("manifest_id and run_id are required.")
    with _file_lock(path):
        data = load_ledger(path)
        if manifest_id in data["entries"]:
            previous = data["entries"][manifest_id]
            raise ValueError(
                f"Manifest already has ledger state '{previous['state']}'; "
                "refusing duplicate delivery. Reconcile uncertain reservations explicitly."
            )
        now = _now()
        entry = {
            "content_type": content_type,
            "state": "reserved",
            "run_id": run_id,
            "created_at": now,
            "updated_at": now,
            "telegram_message_id": None,
        }
        data["entries"][manifest_id] = entry
        save_ledger(path, data)
        return entry



def assert_reserved_for_run(path: Path, manifest_id: str, content_type: str, run_id: str) -> dict[str, Any]:
    """Verify a reservation was persisted before this run is allowed to call Telegram."""
    _require_manifest_id(manifest_id)
    if not isinstance(content_type, str) or content_type not in {"dua", "dhikr"}:
        raise ValueError("Only dua/dhikr can be sent by Pro.")
    if not isinstance(run_id, str) or not run_id.strip():
        raise ValueError("A non-empty run_id is required.")
    with _file_lock(path):
        data = load_ledger(path)
        entry = data["entries"].get(manifest_id)
        if entry is None:
            raise ValueError("No persisted reservation exists; refusing Telegram request.")
        if entry.get("state") != "reserved":
            raise ValueError("Persisted reservation is not in reserved state; refusing Telegram request.")
        if entry.get("run_id") != run_id:
            raise ValueError("Persisted reservation belongs to a different workflow run.")
        if entry.get("content_type") != content_type:
            raise ValueError("Persisted reservation content type does not match the manifest.")
        return dict(entry)


def transition(path: Path, manifest_id: str, new_state: str,
               telegram_message_id: int | None = None) -> dict[str, Any]:
    _require_manifest_id(manifest_id)
    if not isinstance(new_state, str) or new_state not in VALID_STATES:
        raise ValueError(f"state must be one of {sorted(VALID_STATES)}.")
    with _file_lock(path):
        data = load_ledger(path)
        entry = data["entries"].get(manifest_id)
        if entry is None:
            raise ValueError("Manifest has no reservation; refusing an untracked state change.")
        old_state = entry["state"]
        allowed = {
            "reserved": {"delivered", "uncertain"},
            "uncertain": {"delivered"},
            "delivered": set(),
        }
        if new_state not in allowed[old_state]:
            raise ValueError(f"Invalid ledger transition: {old_state} -> {new_state}.")
        if new_state == "delivered":
            if isinstance(telegram_message_id, bool) or not isinstance(telegram_message_id, int) or telegram_message_id <= 0:
                raise ValueError("A confirmed positive Telegram message_id is required for delivered state.")
            entry["telegram_message_id"] = telegram_message_id
        elif telegram_message_id is not None:
            raise ValueError("Telegram message_id is only valid for delivered state.")
        entry["state"] = new_state
        entry["updated_at"] = _now()
        save_ledger(path, data)
        return entry


def reconcile_not_delivered(path: Path, manifest_id: str, confirmation: str) -> None:
    """Release only after a human confirms Telegram did not accept the video."""
    _require_manifest_id(manifest_id)
    if confirmation != "CONFIRM_NOT_DELIVERED":
        raise ValueError("Explicit CONFIRM_NOT_DELIVERED confirmation is required.")
    with _file_lock(path):
        data = load_ledger(path)
        entry = data["entries"].get(manifest_id)
        if entry is None or entry["state"] not in {"reserved", "uncertain"}:
            raise ValueError("Only reserved/uncertain entries can be reconciled as not delivered.")
        del data["entries"][manifest_id]
        save_ledger(path, data)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path, default=Path("data/pro_delivery_ledger.json"))
    sub = parser.add_subparsers(dest="command", required=True)
    reserve_parser = sub.add_parser("reserve")
    reserve_parser.add_argument("--manifest-id", required=True)
    reserve_parser.add_argument("--content-type", choices=("dua", "dhikr"), required=True)
    reserve_parser.add_argument("--run-id", required=True)
    state_parser = sub.add_parser("transition")
    state_parser.add_argument("--manifest-id", required=True)
    state_parser.add_argument("--state", choices=tuple(sorted(VALID_STATES)), required=True)
    state_parser.add_argument("--telegram-message-id", type=int)
    reconcile_parser = sub.add_parser("reconcile-not-delivered")
    reconcile_parser.add_argument("--manifest-id", required=True)
    reconcile_parser.add_argument("--confirm", required=True)
    args = parser.parse_args()
    if args.command == "reserve":
        result = reserve(args.ledger, args.manifest_id, args.content_type, args.run_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "transition":
        result = transition(args.ledger, args.manifest_id, args.state, args.telegram_message_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        reconcile_not_delivered(args.ledger, args.manifest_id, args.confirm)
        print("Reservation explicitly reconciled as not delivered.")


if __name__ == "__main__":
    main()
