"""Choose only reviewed assets while avoiding recent repeats."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable


def _validated_recent_ids(recent_ids: Iterable[str]) -> set[str]:
    if isinstance(recent_ids, (str, bytes)):
        raise ValueError("recent_ids must be an iterable of strings, not a single string.")
    try:
        values = list(recent_ids)
    except TypeError:
        raise ValueError("recent_ids must be an iterable of strings.") from None
    if any(not isinstance(value, str) for value in values):
        raise ValueError("recent_ids must contain only strings.")
    return set(values)


def choose_asset(catalog_path: Path, asset_kind: str, recent_ids: Iterable[str] = (),
                 rotation_key: str = "") -> dict:
    if not isinstance(asset_kind, str) or asset_kind not in {"background", "audio"}:
        raise ValueError("asset_kind must be background or audio.")
    if not isinstance(rotation_key, str):
        raise ValueError("rotation_key must be a string.")
    recent = _validated_recent_ids(recent_ids)
    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        raise ValueError("Cannot read asset catalog as valid UTF-8 JSON.") from None
    if not isinstance(catalog, dict):
        raise ValueError("Asset catalog must be a JSON object.")
    entries = catalog.get(asset_kind, [])
    if not isinstance(entries, list):
        raise ValueError(f"Asset catalog '{asset_kind}' entries must be a list.")
    eligible = []
    for item in entries:
        if not isinstance(item, dict):
            continue
        asset_id = item.get("id")
        if not isinstance(asset_id, str) or not asset_id or asset_id in recent:
            continue
        if item.get("approved") is not True or item.get("user_approved") is not True:
            continue
        if item.get("rights_verified") is not True:
            continue
        source_url, asset_url = item.get("source_url"), item.get("asset_url")
        if not isinstance(source_url, str) or not source_url.startswith("https://"):
            continue
        if not isinstance(asset_url, str) or not asset_url.startswith("https://"):
            continue
        eligible.append(item)
    if not eligible:
        raise LookupError(
            f"No approved, rights-verified, non-recent {asset_kind} asset; refusing fallback."
        )
    digest = hashlib.sha256(rotation_key.encode("utf-8")).digest()
    return eligible[int.from_bytes(digest[:8], "big") % len(eligible)]
