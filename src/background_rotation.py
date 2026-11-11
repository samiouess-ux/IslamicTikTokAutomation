"""Deterministic selection of explicitly approved Quran video backgrounds."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Iterable
from urllib.parse import urlsplit



def _is_trusted_pexels_url(value: object, *, media: bool = False) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = urlsplit(value)
        if parsed.scheme != "https" or parsed.username or parsed.password:
            return False
        if parsed.port not in (None, 443) or parsed.query or parsed.fragment:
            return False
        if media:
            return parsed.hostname == "videos.pexels.com" and parsed.path.startswith("/video-files/")
        return parsed.hostname in {"pexels.com", "www.pexels.com"}
    except ValueError:
        return False


def load_eligible_backgrounds(catalog_path: Path) -> list[dict]:
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    candidates = catalog.get("candidates", [])
    eligible = [
        item for item in candidates
        if item.get("approved") is True
        and item.get("user_approved") is True
        and item.get("download_verified") is True
        and _is_trusted_pexels_url(item.get("direct_video_url"), media=True)
        and _is_trusted_pexels_url(item.get("source_page_url"))
    ]
    if not eligible:
        raise ValueError(
            "No explicitly approved, download-verified backgrounds are eligible."
        )
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
    """Select approved clips in deterministic order until duration is covered."""
    if not math.isfinite(required_duration) or required_duration <= 0:
        raise ValueError("Required background duration must be finite and positive.")
    ordered = order_backgrounds(catalog_path, rotation_key, recent_ids)
    selected: list[dict] = []
    total = 0.0
    for item in ordered:
        clip_duration = item.get("duration_seconds")
        # Unknown catalog durations are not evidence of unusable media:
        # the production renderer probes the downloaded file with ffprobe.
        # This duration-only helper skips unknown values rather than failing
        # the entire rotation; the candidate remains eligible elsewhere.
        if (
            isinstance(clip_duration, bool)
            or not isinstance(clip_duration, (int, float))
            or not math.isfinite(float(clip_duration))
            or clip_duration <= 0
        ):
            continue
        selected.append(item)
        total += float(clip_duration)
        if total >= required_duration:
            return selected
    raise ValueError(
        f"Approved backgrounds provide {total:.2f}s, "
        f"short of the required {required_duration:.2f}s."
    )
