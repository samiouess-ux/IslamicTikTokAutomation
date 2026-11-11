"""Ensure the production rotation uses Islamic visuals, not generic nature clips."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from background_rotation import load_eligible_backgrounds


class IslamicBackgroundPriorityTests(unittest.TestCase):
    def test_only_approved_islamic_portrait_candidates_enter_rotation(self):
        candidates = [
            {
                "id": "mosque",
                "category": "mosque_interior",
                "approved": True,
                "user_approved": True,
                "download_verified": True,
                "aspect_ratio": "9:16",
                "direct_video_url": "https://cdn.example/mosque.mp4",
                "source_page_url": "https://example.com/mosque",
            },
            {
                "id": "ocean",
                "category": "sea",
                "approved": True,
                "user_approved": True,
                "download_verified": True,
                "aspect_ratio": "9:16",
                "direct_video_url": "https://cdn.example/ocean.mp4",
                "source_page_url": "https://example.com/ocean",
            },
            {
                "id": "unapproved-mosque",
                "category": "mosque_exterior",
                "approved": True,
                "user_approved": False,
                "download_verified": True,
                "aspect_ratio": "9:16",
                "direct_video_url": "https://cdn.example/unapproved.mp4",
                "source_page_url": "https://example.com/unapproved",
            },
        ]
        with tempfile.TemporaryDirectory() as tmp:
            catalog = Path(tmp) / "catalog.json"
            catalog.write_text(json.dumps({"candidates": candidates}), encoding="utf-8")
            selected = load_eligible_backgrounds(catalog)

        self.assertEqual([item["id"] for item in selected], ["mosque"])

    def test_rotation_fails_closed_when_no_approved_islamic_portrait_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            catalog = Path(tmp) / "catalog.json"
            catalog.write_text(json.dumps({"candidates": []}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Islamic portrait backgrounds"):
                load_eligible_backgrounds(catalog)


if __name__ == "__main__":
    unittest.main()
