"""Review-only adapters for the shared typed Quran background library.

The shared inventory is media-neutral. Preview rendering remains media-specific:
video previews are handled by the existing video review pipeline, while this
module creates still-photo contact sheets with the actual transparent Quran
overlay. Nothing here is used by the scheduled production renderer.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

from background_library import load_background_library


def load_review_inventory(video_catalog_path: Path, photo_manifest_path: Path) -> dict[str, list[dict]]:
    """Load one verified inventory, then split it for media-specific review adapters."""
    assets = load_background_library(video_catalog_path, photo_manifest_path)
    return {
        "videos": [item for item in assets if item["media_type"] == "video"],
        "photos": [item for item in assets if item["media_type"] == "photo"],
    }


def build_photo_review_contact_sheet(
    photos: list[dict],
    overlay_frame: Path,
    destination: Path,
    *,
    cell_width: int = 270,
    columns: int = 3,
) -> dict:
    """Create center-cropped 9:16 photo previews with the real Quran overlay."""
    if not photos:
        raise ValueError("No approved photos are available for review.")
    if cell_width < 90 or columns < 1:
        raise ValueError("Photo review sheet dimensions are invalid.")
    if not overlay_frame.is_file():
        raise FileNotFoundError(f"Quran overlay frame not found: {overlay_frame}")

    cell_height = round(cell_width * 16 / 9)
    label_height = 30
    with Image.open(overlay_frame) as source_overlay:
        overlay = ImageOps.fit(
            source_overlay.convert("RGBA"),
            (cell_width, cell_height),
            method=Image.Resampling.LANCZOS,
            centering=(0.5, 0.5),
        )
    if overlay.getbbox() is None:
        raise ValueError("Quran overlay frame is empty.")

    rows = (len(photos) + columns - 1) // columns
    sheet = Image.new(
        "RGB",
        (columns * cell_width, rows * (cell_height + label_height)),
        (10, 16, 22),
    )
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()

    for index, item in enumerate(photos):
        source_path = Path(item["asset_path"])
        if not source_path.is_file():
            raise FileNotFoundError(f"Approved photo is missing: {source_path}")
        with Image.open(source_path) as source:
            base = ImageOps.fit(
                source.convert("RGBA"),
                (cell_width, cell_height),
                method=Image.Resampling.LANCZOS,
                centering=(0.5, 0.5),
            )
        base.alpha_composite(overlay)
        x = (index % columns) * cell_width
        y = (index // columns) * (cell_height + label_height)
        sheet.paste(base.convert("RGB"), (x, y))
        draw.text(
            (x + 8, y + cell_height + 7),
            str(item["asset_id"])[:36],
            fill=(255, 255, 255),
            font=font,
        )

    destination.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(destination, quality=90)
    return {
        "photo_count": len(photos),
        "columns": columns,
        "cell_size": [cell_width, cell_height],
        "contact_sheet": str(destination),
        "overlay_legibility_review_required": True,
        "production_enabled": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare a review-only contact sheet for the shared Quran background library.")
    parser.add_argument("--video-catalog", type=Path, default=Path("data/background_candidates.json"))
    parser.add_argument("--photo-manifest", type=Path, default=Path("data/background_photos_manifest.json"))
    parser.add_argument("--overlay-frame", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("output/background_additions_review"))
    args = parser.parse_args()

    inventory = load_review_inventory(args.video_catalog, args.photo_manifest)
    photo_report = build_photo_review_contact_sheet(
        inventory["photos"],
        args.overlay_frame,
        args.output_dir / "photo_backgrounds_quran_overlay_contact_sheet.jpg",
    )
    report = {
        "status": "review_only_inventory_and_photo_previews_ready",
        "video_count": len(inventory["videos"]),
        "video_ids": [item["asset_id"] for item in inventory["videos"]],
        "photo_ids": [item["asset_id"] for item in inventory["photos"]],
        **photo_report,
    }
    (args.output_dir / "background_library_review_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"Prepared {report['photo_count']} approved photo previews and "
        f"indexed {report['video_count']} eligible video backgrounds."
    )
    print("Review-only output; scheduled production rendering is unchanged.")


if __name__ == "__main__":
    main()
