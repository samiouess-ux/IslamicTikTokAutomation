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
    if not isinstance(content_type, str) or content_type not in {"quran", "dua", "dhikr"}:
        raise ValueError("Unsupported content type.")
    if not isinstance(rotation_key, str):
        raise ValueError("rotation_key must be a string.")
    recent_values = list(recent_ids)
    if any(not isinstance(value, str) for value in recent_values):
        raise ValueError("recent_ids must contain only strings.")
    recent = set(recent_values)
    eligible: list[tuple[str, Path]] = []
    for path in sorted(content_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        # Valid JSON may still contain a list, scalar, or malformed nested
        # publishing value. Treat those manifests as ineligible, not fatal.
        if not isinstance(data, dict):
            continue
        publishing = data.get("publishing", {})
        if not isinstance(publishing, dict):
            continue
        if data.get("content_type", "quran") != content_type:
            continue
        if data.get("rotation_approved") is not True:
            continue
        if publishing.get("approval_required") is not True:
            continue
        if publishing.get("auto_publish", False):
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


def choose_manifests(
    content_dir: Path,
    content_type: str,
    count: int,
    recent_ids: Iterable[str] = (),
    rotation_key: str = "",
) -> list[Path]:
    """Select a batch of distinct approved manifests or fail without a partial batch."""
    if type(count) is not int or count < 1:
        raise ValueError("count must be a positive integer.")
    if not isinstance(content_type, str) or content_type not in {"quran", "dua", "dhikr"}:
        raise ValueError("Unsupported content type.")
    if not isinstance(rotation_key, str):
        raise ValueError("rotation_key must be a string.")
    recent_values = list(recent_ids)
    if any(not isinstance(value, str) for value in recent_values):
        raise ValueError("recent_ids must contain only strings.")
    recent = set(recent_values)
    selected: list[Path] = []
    for index in range(count):
        try:
            candidate = choose_manifest(
                content_dir, content_type, recent_ids=recent,
                rotation_key=f"{rotation_key}:{index}",
            )
        except FileNotFoundError as exc:
            raise FileNotFoundError(
                f"Cannot build a complete batch of {count} distinct {content_type} manifests; "
                f"selected {len(selected)}. {exc}"
            ) from exc
        try:
            data = json.loads(candidate.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(
                f"Selected manifest changed or became unreadable during batch selection: {candidate}"
            ) from exc
        if not isinstance(data, dict):
            raise ValueError(f"Selected manifest is no longer a JSON object: {candidate}")
        publishing = data.get("publishing", {})
        item_id = data.get("id")
        if (
            data.get("content_type", "quran") != content_type
            or data.get("rotation_approved") is not True
            or not isinstance(publishing, dict)
            or publishing.get("approval_required") is not True
            or publishing.get("auto_publish", False)
            or not isinstance(item_id, str)
            or not item_id
            or item_id in recent
        ):
            raise ValueError(f"Selected manifest is no longer eligible for rotation: {candidate}")
        recent.add(item_id)
        selected.append(candidate)
    return selected
