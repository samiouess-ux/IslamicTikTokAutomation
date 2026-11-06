"""Isolated durable idempotency ledger for Pro candidate Telegram previews."""
from __future__ import annotations

import json
import os
import re
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

VERSION = 1
VALID_STATES = {"reserved", "delivered", "uncertain"}
VALID_TYPES = {"dua", "dhikr"}
ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,79}\Z")
HASH_PATTERN = re.compile(r"[0-9a-f]{64}\Z")


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def file_lock(path: Path) -> Iterator[None]:
    """Serialize local read/modify/write operations; CI concurrency handles runners."""
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


def validate_candidate_id(candidate_id: str) -> None:
    if not isinstance(candidate_id, str) or not ID_PATTERN.fullmatch(candidate_id):
        raise ValueError("candidate_id must be a safe 1-80 character filename component.")


def _validate_entry(key: str, entry: Any) -> None:
    validate_candidate_id(key)
    if not isinstance(entry, dict) or entry.get("candidate_id") != key:
        raise ValueError("Preview ledger entry key/candidate_id mismatch.")
    if entry.get("content_type") not in VALID_TYPES or entry.get("state") not in VALID_STATES:
        raise ValueError("Preview ledger entry has an unsupported content_type or state.")
    for field in ("manifest_sha256", "video_sha256"):
        value = entry.get(field)
        if not isinstance(value, str) or not HASH_PATTERN.fullmatch(value):
            raise ValueError(f"{field} must be a lowercase SHA-256 hex digest.")
    for field in ("workflow_run_id", "created_at", "updated_at"):
        value = entry.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} is required.")
    message_id = entry.get("telegram_message_id")
    if entry["state"] == "delivered":
        if isinstance(message_id, bool) or not isinstance(message_id, int) or message_id <= 0:
            raise ValueError("Delivered preview requires a positive integer Telegram message_id.")
    elif message_id is not None:
        raise ValueError("telegram_message_id must be null until delivery is confirmed.")


def validate_ledger(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict) or set(data) != {"version", "entries"}:
        raise ValueError("Preview ledger must contain exactly version and entries.")
    if type(data["version"]) is not int or data["version"] != VERSION:
        raise ValueError("Unsupported preview ledger schema version.")
    if not isinstance(data["entries"], dict):
        raise ValueError("Preview ledger entries must be an object.")
    for key, entry in data["entries"].items():
        _validate_entry(key, entry)
    return data


def load_ledger(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"version": VERSION, "entries": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot read Pro preview ledger: {exc}") from exc
    return validate_ledger(data)


def save_ledger(path: Path, data: dict[str, Any]) -> None:
    validate_ledger(data)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        try:
            directory_fd = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
        except OSError:
            pass
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def reserve(path: Path, candidate_id: str, content_type: str, manifest_sha256: str,
            video_sha256: str, workflow_run_id: str) -> dict[str, Any]:
    validate_candidate_id(candidate_id)
    if content_type not in VALID_TYPES:
        raise ValueError("Only dua/dhikr candidates can be preview-sent.")
    if not isinstance(workflow_run_id, str) or not workflow_run_id.strip():
        raise ValueError("workflow_run_id is required.")
    now = now_utc()
    entry = {
        "candidate_id": candidate_id,
        "content_type": content_type,
        "manifest_sha256": manifest_sha256,
        "video_sha256": video_sha256,
        "workflow_run_id": workflow_run_id,
        "state": "reserved",
        "created_at": now,
        "updated_at": now,
        "telegram_message_id": None,
    }
    _validate_entry(candidate_id, entry)
    with file_lock(path):
        data = load_ledger(path)
        previous = data["entries"].get(candidate_id)
        if previous is not None:
            if (previous["manifest_sha256"], previous["video_sha256"]) != (manifest_sha256, video_sha256):
                raise ValueError("Candidate ID already exists with different hashes; identity conflict.")
            raise ValueError(f"Candidate already has preview ledger state '{previous['state']}'; refusing duplicate send.")
        data["entries"][candidate_id] = entry
        save_ledger(path, data)
    return dict(entry)


def transition(path: Path, candidate_id: str, state: str, message_id: int | None = None) -> dict[str, Any]:
    if state not in {"delivered", "uncertain"}:
        raise ValueError("Only delivered or uncertain transitions are supported.")
    with file_lock(path):
        data = load_ledger(path)
        entry = data["entries"].get(candidate_id)
        if entry is None:
            raise ValueError("Unknown preview candidate reservation.")
        if entry["state"] == "reserved":
            pass
        elif entry["state"] == "uncertain" and state == "delivered":
            pass  # caller must supply a recovered Telegram receipt
        else:
            raise ValueError(f"Invalid preview ledger transition {entry['state']} -> {state}.")
        if state == "delivered":
            if isinstance(message_id, bool) or not isinstance(message_id, int) or message_id <= 0:
                raise ValueError("Delivered state requires a positive integer Telegram message_id.")
            entry["telegram_message_id"] = message_id
        else:
            if message_id is not None:
                raise ValueError("Uncertain state must not carry a Telegram message_id.")
            entry["telegram_message_id"] = None
        entry["state"] = state
        entry["updated_at"] = now_utc()
        save_ledger(path, data)
        return dict(entry)
