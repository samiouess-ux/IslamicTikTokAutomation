"""Tests for the shared typed photo/video background library."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from background_library import load_background_library


class BackgroundLibraryTests(unittest.TestCase):
    def test_combines_only_eligible_assets_and_preserves_media_type(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            photo = root / "approved.jpg"
            Image.effect_noise((900, 1200), 100).convert("RGB").save(photo, quality=95)
            videos = root / "videos.json"
            videos.write_text(json.dumps({"candidates": [
                {
                    "id": "video-1", "approved": True, "user_approved": True,
                    "download_verified": True, "aspect_ratio": "9:16",
                    "direct_video_url": "https://cdn.example/video.mp4",
                    "source_page_url": "https://example.com/video"
                },
                {
                    "id": "video-pending", "approved": True, "user_approved": True,
                    "download_verified": False, "aspect_ratio": "9:16",
                    "direct_video_url": "https://cdn.example/pending.mp4",
                    "source_page_url": "https://example.com/pending"
                }
            ]}), encoding="utf-8")
            photos = root / "photos.json"
            photos.write_text(json.dumps({
                "user_approval": {
                    "status": "approved", "user_approved": True,
                    "approval_scope": "test allowlist"
                },
                "approved_photo_ids": ["photo-1"],
                "candidates": [
                    {"id": "photo-1", "local_path": str(photo),
                     "source_page_url": "https://example.com/photo",
                     "image_url": "https://cdn.example/photo.jpg"},
                    {"id": "photo-missing", "local_path": str(root / "missing.jpg")}
                ]
            }), encoding="utf-8")

            items = load_background_library(videos, photos)
            self.assertEqual({(x["media_type"], x["asset_id"]) for x in items}, {
                ("photo", "photo-1"), ("video", "video-1")
            })
            self.assertEqual(next(x for x in items if x["media_type"] == "photo")["asset_path"],
                             str(photo))
            self.assertEqual(next(x for x in items if x["media_type"] == "video")["asset_url"],
                             "https://cdn.example/video.mp4")

    def test_rejects_duplicate_ids_across_media_types(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            photo = root / "same.jpg"
            Image.effect_noise((900, 1200), 100).convert("RGB").save(photo, quality=95)
            videos = root / "videos.json"
            videos.write_text(json.dumps({"candidates": [{
                "id": "same", "approved": True, "user_approved": True,
                "download_verified": True, "aspect_ratio": "9:16",
                "direct_video_url": "https://cdn.example/video.mp4",
                "source_page_url": "https://example.com/video"
            }]}), encoding="utf-8")
            photos = root / "photos.json"
            photos.write_text(json.dumps({
                "user_approval": {
                    "status": "approved", "user_approved": True,
                    "approval_scope": "test allowlist"
                },
                "approved_photo_ids": ["same"],
                "candidates": [{
                    "id": "same", "local_path": str(photo),
                    "source_page_url": "https://example.com/photo",
                    "image_url": "https://cdn.example/photo.jpg"
                }]
            }), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "globally unique"):
                load_background_library(videos, photos)


if __name__ == "__main__":
    unittest.main()
