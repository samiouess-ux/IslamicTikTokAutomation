"""Tests for approved asset selection and fail-closed repeat protection."""
import json
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from asset_rotation import choose_asset


class AssetRotationTests(unittest.TestCase):
    def test_selects_approved_asset_not_recent(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "assets.json"
            entries = [
                {"id": "used", "approved": True, "user_approved": True,
                 "rights_verified": True, "source_url": "https://source.test",
                 "asset_url": "https://asset.test/1"},
                {"id": "fresh", "approved": True, "user_approved": True,
                 "rights_verified": True, "source_url": "https://source.test",
                 "asset_url": "https://asset.test/2"}
            ]
            path.write_text(json.dumps({"background": entries}), encoding="utf-8")
            self.assertEqual(choose_asset(path, "background", ["used"], "daily-1")["id"], "fresh")

    def test_rejects_malformed_catalog_shapes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "assets.json"
            path.write_text('["not", "an", "object"]', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "catalog must be a JSON object"):
                choose_asset(path, "background")
            path.write_text(json.dumps({"background": {"id": "not-a-list"}}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "entries must be a list"):
                choose_asset(path, "background")

    def test_rejects_malformed_rotation_arguments(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "assets.json"
            path.write_text(json.dumps({"background": []}), encoding="utf-8")
            for kind in ([], {}, 7, True):
                with self.subTest(asset_kind=kind), self.assertRaisesRegex(ValueError, "asset_kind"):
                    choose_asset(path, kind)
            for recent in ("one-id", b"bytes", None, [["nested"]], [None]):
                with self.subTest(recent_ids=recent), self.assertRaisesRegex(ValueError, "recent_ids"):
                    choose_asset(path, "background", recent_ids=recent)
            with self.assertRaisesRegex(ValueError, "rotation_key"):
                choose_asset(path, "background", rotation_key=[])

    def test_rejects_unapproved_or_unlicensed_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "assets.json"
            path.write_text(json.dumps({"audio": [
                {"id": "bad", "approved": True, "user_approved": True,
                 "rights_verified": False, "source_url": "https://source.test",
                 "asset_url": "https://asset.test/audio"}
            ]}), encoding="utf-8")
            with self.assertRaisesRegex(LookupError, "refusing fallback"):
                choose_asset(path, "audio", rotation_key="daily-1")


if __name__ == "__main__":
    unittest.main()
