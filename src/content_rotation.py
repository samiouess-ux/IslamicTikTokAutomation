"""Deterministic content rotation with recent-repeat protection.

Only reviewed manifests are eligible. This module chooses existing files; it
never invents Quran verses, duas, translations, audio, or background assets.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable


def choose_manifest(
    content_dir: Path,
    content_type: str,
    recent_ids: Iterable[str] = (),
    rotation_key: str = "",
) -> Path:
    if content_type not in {"quran", "dua", "dhikr"}:
        raise ValueError("Unsupported content type.")
    recent = set(recent_ids)
    eligible: list[tuple[str, Path]] = []
    for path in sorted(content_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if data.get("content_type", "quran") != content_type:
            continue
        if data.get("status") not in {"approved", "reviewed", "ready_for_review",
                                      "rendered_prototype_user_positive_reusable_pipeline_next"}:
            continue
        if data.get("publishing", {}).get("approval_required") is not True:
            continue
        if data.get("publishing", {}).get("auto_publish", False):
            continue
        item_id = data.get("id")
        if isinstance(item_id, str) and item_id and item_id not in recent:
            eligible.append((item_id, path))
    if not eligible:
        raise FileNotFoundError(
            f"No eligible non-recent {content_type} manifest; refusing to repeat or invent content."
        )
    digest = hashlib.sha256(rotation_key.encode("utf-8")).digest()
    return eligible[int.from_bytes(digest[:8], "big") % len(eligible)][1]
