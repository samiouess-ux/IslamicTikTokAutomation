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
        and item.get("aspect_ratio") == "9:16"
        and isinstance(item.get("direct_video_url"), str)
        and item["direct_video_url"].startswith("https://")
        and isinstance(item.get("source_page_url"), str)
        and item["source_page_url"].startswith("https://")
    ]
    if not eligible:
        raise ValueError("No explicitly approved, download-verified 9:16 portrait backgrounds are eligible.")
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
    recent = set(recent_ids)
    fresh = [item for item in eligible if item["id"] != first["id"] and item["id"] not in recent]
    previously_used = [item for item in eligible if item["id"] != first["id"] and item["id"] in recent]

    def order_key(item: dict) -> str:
        return hashlib.sha256(
            f"{rotation_key}:{first['id']}:{item['id']}".encode("utf-8")
        ).hexdigest()

    fresh.sort(key=order_key)
    previously_used.sort(key=order_key)
    return [first, *fresh, *previously_used]



def select_background_sequence(
    catalog_path: Path,
    rotation_key: str,
    required_duration: float,
    recent_ids: Iterable[str] = (),
) -> list[dict]:
    """Select approved portrait clips in deterministic order until duration is covered."""
    if required_duration <= 0:
        raise ValueError("Required background duration must be positive.")
    ordered = order_backgrounds(catalog_path, rotation_key, recent_ids)
    selected: list[dict] = []
    total = 0.0
    for item in ordered:
        clip_duration = item.get("duration_seconds")
        if not isinstance(clip_duration, (int, float)) or clip_duration <= 0:
            raise ValueError(f"Background {item.get('id', '<unknown>')} has no verified positive duration.")
        selected.append(item)
        total += float(clip_duration)
        if total >= required_duration:
            return selected
    raise ValueError(
        f"Approved portrait backgrounds provide {total:.2f}s, "
        f"short of the required {required_duration:.2f}s."
    )


def load_eligible_photo_backgrounds(manifest_path: Path) -> list[dict]:
    """Load previously user-approved photos only when their local image files verify."""
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    approved_ids = manifest.get("approved_photo_ids", [])
    if not isinstance(approved_ids, list) or not approved_ids:
        raise ValueError("Photo manifest has no explicit approved_photo_ids allowlist.")
    if any(not isinstance(item_id, str) or not item_id.strip() for item_id in approved_ids):
        raise ValueError("Photo approved_photo_ids must contain non-empty strings.")
    if len(approved_ids) != len(set(approved_ids)):
        raise ValueError("Photo approved_photo_ids must be unique.")
    approved_id_set = set(approved_ids)

    from PIL import Image

    candidates = manifest.get("candidates", [])
    eligible = []
    for item in candidates:
        if item.get("id") not in approved_id_set:
            continue
        local_path = item.get("local_path")
        if not isinstance(local_path, str) or not local_path.strip():
            continue
        path = Path(local_path)
        if not path.is_file() or path.stat().st_size < 50_000:
            continue
        try:
            with Image.open(path) as image:
                image.verify()
            with Image.open(path) as image:
                width, height = image.size
                if width < 720 or height < 720:
                    continue
        except (OSError, ValueError):
            continue
        eligible.append(item)
    ids = [item.get("id") for item in eligible]
    if any(not item_id for item_id in ids) or len(ids) != len(set(ids)):
        raise ValueError("Eligible photo background IDs must be present and unique.")
    if not eligible:
        raise ValueError("No previously approved photo backgrounds passed local image verification.")
    return sorted(eligible, key=lambda item: item["id"])
