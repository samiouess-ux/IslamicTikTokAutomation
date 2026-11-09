"""Isolated, persistent rotation for reviewed opening-cover assets.

This module is not wired into the production renderer yet. It is safe to test
independently before any production integration is approved.
"""
from __future__ import annotations

import json
from pathlib import Path


def _read_json(path: Path, default: dict) -> dict:
    if not path.exists():
        return dict(default)
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cover rotation state/catalog is unreadable: {path}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return value


def _atomic_write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def choose_cover(
    catalog_path: Path,
    state_path: Path,
    video_key: str,
    original_cover_id: str = "original",
) -> dict:
    """Choose an approved existing cover, never repeating consecutively.

    Repeating the same video_key is idempotent: a render retry reuses its
    recorded cover instead of advancing rotation a second time.
    """
    if not isinstance(video_key, str) or not video_key.strip():
        raise ValueError("video_key must be a non-empty stable video identifier.")

    catalog = _read_json(Path(catalog_path), {"covers": []})
    entries = catalog.get("covers")
    if not isinstance(entries, list):
        raise ValueError("Cover catalog field 'covers' must be a list.")

    eligible: list[dict] = []
    seen: set[str] = set()
    for item in entries:
        if not isinstance(item, dict):
            continue
        cover_id = item.get("id")
        asset_path = item.get("asset_path")
        if not isinstance(cover_id, str) or not cover_id or cover_id in seen:
            continue
        seen.add(cover_id)
        if item.get("approved") is not True or not isinstance(asset_path, str):
            continue
        if not Path(asset_path).is_file():
            continue
        eligible.append(dict(item))

    original = next((item for item in eligible if item["id"] == original_cover_id), None)
    if original is None:
        raise LookupError("The original approved cover is missing; refusing unsafe fallback.")
    if not eligible:
        raise LookupError("No approved cover is available.")

    state = _read_json(Path(state_path), {"schema_version": 1, "last_cover_id": None,
                                          "last_video_key": None})
    if state.get("schema_version") != 1:
        raise ValueError("Unsupported cover rotation state schema.")
    if state.get("last_video_key") == video_key:
        previous_id = state.get("last_cover_id")
        previous = next((item for item in eligible if item["id"] == previous_id), None)
        if previous is not None:
            return previous

    previous_id = state.get("last_cover_id")
    fresh = [item for item in eligible if item["id"] != previous_id]
    # With multiple eligible covers this guarantees a different consecutive
    # choice. With only the original available, keep the system operational.
    pool = fresh or [original]
    selected = pool[0]

    _atomic_write(Path(state_path), {
        "schema_version": 1,
        "last_cover_id": selected["id"],
        "last_video_key": video_key,
    })
    return selected
