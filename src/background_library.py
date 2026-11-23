"""Shared, fail-closed intake for approved photo and video backgrounds.

This module normalizes catalog records for review and management only. Rendering
remains media-specific: callers must use the photo or video renderer adapter.
"""
from __future__ import annotations

from pathlib import Path

from background_rotation import (
    load_eligible_backgrounds,
    load_eligible_photo_backgrounds,
)


def load_background_library(
    video_catalog_path: Path,
    photo_manifest_path: Path,
) -> list[dict]:
    """Return verified, user-approved photo and video assets in one typed list."""
    videos = load_eligible_backgrounds(video_catalog_path)
    photos = load_eligible_photo_backgrounds(photo_manifest_path)

    normalized: list[dict] = []
    for item in videos:
        normalized.append({
            **item,
            "media_type": "video",
            "asset_id": item["id"],
            "source_url": item["source_page_url"],
            "asset_url": item["direct_video_url"],
            "asset_path": None,
        })
    for item in photos:
        normalized.append({
            **item,
            "media_type": "photo",
            "asset_id": item["id"],
            "source_url": item["source_page_url"],
            "asset_url": item.get("image_url"),
            "asset_path": item["local_path"],
        })

    ids = [item["asset_id"] for item in normalized]
    if len(ids) != len(set(ids)):
        raise ValueError("Background asset IDs must be globally unique across media types.")
    return sorted(normalized, key=lambda item: (item["media_type"], item["asset_id"]))
