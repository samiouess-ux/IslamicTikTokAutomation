"""Regression tests for applying background rotation before manifest validation."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from render_video_scenes import prepare_manifest_background


class RendererBackgroundPreparationTests(unittest.TestCase):
    def _manifest(self):
        return {
            "visual": {
                "background_candidate": {
                    "id": "stale-manifest-background",
                    "download_verified": False,
                },
                "approved_background_url": "https://example.com/stale.mp4",
            }
        }

    @patch("render_video_scenes.validate_content_manifest")
    @patch("background_rotation.order_backgrounds")
    def test_rotation_replaces_stale_background_before_validation(
        self, order_backgrounds, validate_manifest
    ):
        selected = {
            "id": "verified-catalog-background",
            "direct_video_url": "https://cdn.example/verified.mp4",
            "source_page_url": "https://example.com/source",
            "approved": True,
            "user_approved": True,
            "download_verified": True,
            "aspect_ratio": "9:16",
            "duration_seconds": 12,
        }
        order_backgrounds.return_value = [selected]

        manifest = self._manifest()
        sequence = prepare_manifest_background(
            manifest, True, "stable-key", ["recent-id"]
        )

        self.assertEqual(sequence[0]["id"], selected["id"])
        self.assertEqual(
            manifest["visual"]["background_candidate"]["id"], selected["id"]
        )
        self.assertEqual(
            manifest["visual"]["background_candidate"]["source_url"],
            selected["source_page_url"],
        )
        self.assertNotIn("approved_background_url", manifest["visual"])
        validate_manifest.assert_called_once_with(manifest)
        order_backgrounds.assert_called_once_with(
            Path("data/background_candidates.json"), "stable-key", ["recent-id"]
        )

    @patch("render_video_scenes.validate_content_manifest")
    @patch("background_rotation.order_backgrounds")
    def test_rotation_keeps_approved_candidate_with_unreported_catalog_duration(
        self, order_backgrounds, validate_manifest
    ):
        selected = {
            "id": "approved-duration-probed-at-runtime",
            "direct_video_url": "https://cdn.example/verified.mp4",
            "source_page_url": "https://example.com/source",
            "approved": True,
            "user_approved": True,
            "download_verified": True,
            "duration_seconds": None,
        }
        order_backgrounds.return_value = [selected]

        sequence = prepare_manifest_background(
            self._manifest(), True, "stable-key", []
        )

        self.assertEqual(sequence[0]["id"], selected["id"])
        self.assertIsNone(sequence[0]["duration_seconds"])
        self.assertEqual(
            sequence[0]["direct_video_url"], "https://cdn.example/verified.mp4"
        )
        validate_manifest.assert_called_once()

    @patch("render_video_scenes.validate_content_manifest")
    def test_without_rotation_validation_keeps_original_manifest(self, validate_manifest):
        manifest = self._manifest()

        sequence = prepare_manifest_background(manifest, False, "unused", [])

        self.assertIsNone(sequence)
        self.assertEqual(
            manifest["visual"]["background_candidate"]["id"],
            "stale-manifest-background",
        )
        validate_manifest.assert_called_once_with(manifest)

    @patch("render_video_scenes.validate_content_manifest")
    def test_rotation_rejects_non_object_visual_before_catalog_selection(
        self, validate_manifest
    ):
        manifest = {"visual": []}

        with self.assertRaisesRegex(SystemExit, "visual must be an object"):
            prepare_manifest_background(manifest, True, "stable-key", [])

        validate_manifest.assert_not_called()


if __name__ == "__main__":
    unittest.main()
