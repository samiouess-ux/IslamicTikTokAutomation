"""Tests for the review-only adapter over the shared Quran background library."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from background_review_adapter import (
    build_photo_review_contact_sheet,
    load_review_inventory,
)


class BackgroundReviewAdapterTests(unittest.TestCase):
    def _write_catalogs(self, root: Path):
        photo = root / "approved.jpg"
        Image.effect_noise((1200, 800), 100).convert("RGB").save(photo, quality=95)
        video_catalog = root / "videos.json"
        video_catalog.write_text(json.dumps({"candidates": [{
            "id": "video-1", "approved": True, "user_approved": True,
            "download_verified": True, "aspect_ratio": "9:16",
            "direct_video_url": "https://cdn.example/video.mp4",
            "source_page_url": "https://example.com/video",
        }]}), encoding="utf-8")
        photo_manifest = root / "photos.json"
        photo_manifest.write_text(json.dumps({
            "user_approval": {
                "status": "approved", "user_approved": True,
                "approval_scope": "All 35 photo candidates in this manifest",
            },
            "candidates": [{
                "id": "photo-1", "local_path": str(photo),
                "source_page_url": "https://example.com/photo",
                "image_url": "https://cdn.example/photo.jpg",
            }],
        }), encoding="utf-8")
        return video_catalog, photo_manifest, photo

    def test_inventory_keeps_photos_and_videos_in_separate_groups(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            videos, photos, _ = self._write_catalogs(root)
            inventory = load_review_inventory(videos, photos)
            self.assertEqual([item["asset_id"] for item in inventory["videos"]], ["video-1"])
            self.assertEqual([item["asset_id"] for item in inventory["photos"]], ["photo-1"])
            self.assertEqual(inventory["videos"][0]["media_type"], "video")
            self.assertEqual(inventory["photos"][0]["media_type"], "photo")

    def test_photo_adapter_creates_center_cropped_quran_overlay_sheet_review_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            videos, photos, photo_path = self._write_catalogs(root)
            inventory = load_review_inventory(videos, photos)
            overlay = root / "overlay.png"
            layer = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
            ImageDraw.Draw(layer).rectangle((100, 100, 980, 220), fill=(255, 215, 0, 180))
            layer.save(overlay)
            destination = root / "review" / "photos.jpg"

            report = build_photo_review_contact_sheet(
                inventory["photos"], overlay, destination, cell_width=90, columns=1
            )
            self.assertTrue(destination.is_file())
            with Image.open(destination) as result:
                self.assertEqual(result.size, (90, 190))
            self.assertEqual(report["photo_count"], 1)
            self.assertTrue(report["overlay_legibility_review_required"])
            self.assertFalse(report["production_enabled"])

    def test_photo_adapter_fails_closed_for_empty_inventory(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "No approved photos"):
                build_photo_review_contact_sheet(
                    [], Path(tmp) / "missing.png", Path(tmp) / "out.jpg"
                )


if __name__ == "__main__":
    unittest.main()
