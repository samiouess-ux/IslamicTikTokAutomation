"""Regression tests for content-type-specific safety gates."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from validate_content_manifest import validate_content_manifest


class ContentManifestTests(unittest.TestCase):
    def test_existing_quran_manifest_remains_compatible(self):
        data = json.loads((ROOT / "content/first_video.json").read_text(encoding="utf-8"))
        validate_content_manifest(data)

    def dua_manifest(self):
        return {
            "content_type": "dua",
            "source": {"collection": "review_pending"},
            "items": [{
                "arabic": "نص دعاء تجريبي غير مخصص للإنتاج",
                "source_name": "Test source",
                "source_url": "https://example.org/test"
            }],
            "audio": {
                "kind": "ambient_nature", "approved": True,
                "rights_verified": True, "user_approved": True,
                "music_allowed": False
            },
            "visual": {
                "template": "ornate_gold_classic",
                "background_candidate": {
                    "source_url": "https://example.org/background",
                    "direct_video_url": "https://example.org/background.mp4",
                    "approved": True, "user_approved": True
                }
            },
            "publishing": {"approval_required": True, "auto_publish": False}
        }

    def test_sourced_dua_with_approved_ambient_audio_passes(self):
        validate_content_manifest(self.dua_manifest())

    def test_dua_without_source_is_rejected(self):
        data = self.dua_manifest()
        data["items"][0]["source_url"] = ""
        with self.assertRaisesRegex(SystemExit, "HTTPS religious source"):
            validate_content_manifest(data)

    def test_dua_cannot_use_quran_recitation_audio_kind(self):
        data = self.dua_manifest()
        data["audio"]["kind"] = "quran_recitation"
        with self.assertRaisesRegex(SystemExit, "must not be mislabeled"):
            validate_content_manifest(data)

    def test_unapproved_background_is_rejected(self):
        data = self.dua_manifest()
        data["visual"]["background_candidate"]["user_approved"] = False
        with self.assertRaisesRegex(SystemExit, "Background must be approved"):
            validate_content_manifest(data)

    def test_auto_publish_is_always_rejected(self):
        data = self.dua_manifest()
        data["publishing"]["auto_publish"] = True
        with self.assertRaisesRegex(SystemExit, "Auto-publishing"):
            validate_content_manifest(data)


if __name__ == "__main__":
    unittest.main()
