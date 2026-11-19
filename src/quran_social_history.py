"""Persistent rotation history for social copy; separate from Quran ayah delivery history."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


EMPTY = {"schema_version": 1, "posts": []}


def load_history(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"schema_version": 1, "posts": []}
    history = json.loads(path.read_text(encoding="utf-8"))
    if (
        not isinstance(history, dict)
        or history.get("schema_version") != 1
        or not isinstance(history.get("posts"), list)
    ):
        raise ValueError("Social-content history is malformed or unsupported.")
    return history


def record_post(history: dict[str, Any], candidate_id: str, caption: dict[str, Any]) -> dict[str, Any]:
    if history.get("schema_version") != 1 or not isinstance(history.get("posts"), list):
        raise ValueError("Social-content history is malformed or unsupported.")
    if not isinstance(candidate_id, str) or not candidate_id.strip():
        raise ValueError("A stable non-empty candidate id is required.")
    ar_tags = caption.get("hashtags_ar")
    en_tags = caption.get("hashtags_en")
    hook_id, cta_id = caption.get("hook_id"), caption.get("cta_id")
    if (
        not isinstance(ar_tags, list) or len(ar_tags) != 3
        or not isinstance(en_tags, list) or len(en_tags) != 2
        or len(set(ar_tags + en_tags)) != 5
        or not all(isinstance(tag, str) and tag.startswith("#") for tag in ar_tags + en_tags)
        or not isinstance(hook_id, str) or not hook_id
        or not isinstance(cta_id, str) or not cta_id
    ):
        raise ValueError("Caption does not contain the required five bilingual hashtags and rotation ids.")
    existing = next((post for post in history["posts"] if post.get("candidate_id") == candidate_id), None)
    entry = {
        "candidate_id": candidate_id,
        "hashtags_ar": ar_tags,
        "hashtags_en": en_tags,
        "hook_ids": [hook_id],
        "cta_ids": [cta_id],
    }
    if existing:
        comparable = {key: existing.get(key) for key in entry}
        if comparable != entry:
            raise ValueError("Candidate id already exists with different social content; refusing overwrite.")
        return history
    history["posts"].append({
        **entry,
        "confirmed_at_utc": datetime.now(timezone.utc).isoformat(),
    })
    return history


def save_history(history: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(history, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["record"])
    parser.add_argument("--history", type=Path, required=True)
    parser.add_argument("--caption", type=Path, required=True)
    parser.add_argument("--candidate-id", required=True)
    args = parser.parse_args()
    history = load_history(args.history)
    caption = json.loads(args.caption.read_text(encoding="utf-8"))
    record_post(history, args.candidate_id, caption)
    save_history(history, args.history)
    print(f"Recorded social-content rotation after confirmed Telegram delivery: {args.candidate_id}")


if __name__ == "__main__":
    main()
