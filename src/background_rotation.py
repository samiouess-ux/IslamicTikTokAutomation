"""Deterministic selection of explicitly approved Quran video backgrounds."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable


def load_eligible_backgrounds(catalog_path: Path) -> list[dict]:
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    candidates = catalog.get("candidates", [])
    eligible = [
        item for item in candidates
        if item.get("approved") is True
        and item.get("user_approved") is True
        and item.get("download_verified") is True
        and isinstance(item.get("direct_video_url"), str)
        and item["direct_video_url"].startswith("https://")
        and isinstance(item.get("source_page_url"), str)
        and item["source_page_url"].startswith("https://")
    ]
    if not eligible:
        raise ValueError("No explicitly approved and download-verified backgrounds are eligible.")
    ids = [item.get("id") for item in eligible]
    if any(not item_id for item_id in ids) or len(ids) != len(set(ids)):
        raise ValueError("Eligible background IDs must be present and unique.")
    return sorted(eligible, key=lambda item: item["id"])


def select_background(
    catalog_path: Path,
    rotation_key: str,
    recent_ids: Iterable[str] = (),
) -> dict:
    """Choose a stable candidate while avoiding recently used IDs when possible."""
    if not rotation_key.strip():
        raise ValueError("A non-empty rotation key is required.")
    eligible = load_eligible_backgrounds(catalog_path)
    recent = set(recent_ids)
    fresh = [item for item in eligible if item["id"] not in recent]
    pool = fresh or eligible
    digest = hashlib.sha256(rotation_key.encode("utf-8")).digest()
    return pool[int.from_bytes(digest[:8], "big") % len(pool)]



def order_backgrounds(
    catalog_path: Path,
    rotation_key: str,
    recent_ids: Iterable[str] = (),
) -> list[dict]:
    """Return a deterministic per-video sequence, starting with the rotated pick."""
    eligible = load_eligible_backgrounds(catalog_path)
    first = select_background(catalog_path, rotation_key, recent_ids)
    remainder = [item for item in eligible if item["id"] != first["id"]]
    remainder.sort(
        key=lambda item: hashlib.sha256(
            f"{rotation_key}:{first['id']}:{item['id']}".encode("utf-8")
        ).hexdigest()
    )
    return [first, *remainder]
