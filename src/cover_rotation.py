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
    # Keep a bounded per-video assignment history. A retry may happen after
    # later videos have already advanced the rotation, so last_video_key alone
    # is not enough to guarantee stable cover selection.
    assignments = state.get("video_assignments", {})
    if not isinstance(assignments, dict):
        raise ValueError("Cover rotation state field 'video_assignments' must be an object.")
    assigned_id = assignments.get(video_key)
    if assigned_id is not None:
        assigned = next((item for item in eligible if item["id"] == assigned_id), None)
        if assigned is None:
            raise LookupError(
                f"The previously assigned cover '{assigned_id}' for {video_key} "
                "is no longer eligible; refusing to change this video's cover on retry."
            )
        return assigned

    # Backward compatibility with state written before per-video history existed.
    if state.get("last_video_key") == video_key:
        previous_id = state.get("last_cover_id")
        previous = next((item for item in eligible if item["id"] == previous_id), None)
        if previous is not None:
            return previous

    previous_id = state.get("last_cover_id")
    # Walk the approved catalog in order so every approved design is reached;
    # merely choosing the first non-previous item would starve later variants.
    previous_index = next(
        (index for index, item in enumerate(eligible) if item["id"] == previous_id),
        None,
    )
    if len(eligible) == 1:
        selected = original
    elif previous_index is None:
        selected = original
    else:
        selected = eligible[(previous_index + 1) % len(eligible)]

    assignments[video_key] = selected["id"]
    # Prevent the state file growing without bound while retaining a useful
    # retry window for recent and delayed workflow reruns.
    while len(assignments) > 500:
        oldest_key = next(iter(assignments))
        del assignments[oldest_key]
    _atomic_write(Path(state_path), {
        "schema_version": 1,
        "last_cover_id": selected["id"],
        "last_video_key": video_key,
        "video_assignments": assignments,
    })
    return selected
