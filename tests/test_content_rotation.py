"""Tests for deterministic reviewed-content rotation."""
import json
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from content_rotation import choose_manifest, choose_manifests


class ContentRotationTests(unittest.TestCase):
    def write(self, folder, name, item_id, approved=True, kind="quran"):
        path = folder / name
        path.write_text(json.dumps({
            "id": item_id, "content_type": kind, "rotation_approved": approved,
            "publishing": {"approval_required": True, "auto_publish": False}
        }), encoding="utf-8")
        return path

    def test_selects_approved_non_recent_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            old = self.write(folder, "a.json", "old")
            fresh = self.write(folder, "b.json", "fresh")
            self.assertEqual(choose_manifest(folder, "quran", ["old"], "day-1"), fresh)

    def test_refuses_unreviewed_or_recent_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            self.write(folder, "a.json", "draft", approved=False)
            self.write(folder, "b.json", "seen")
            with self.assertRaisesRegex(FileNotFoundError, "refusing to repeat"):
                choose_manifest(folder, "quran", ["seen"], "day-1")

    def test_separates_content_types(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            dua = self.write(folder, "dua.json", "dua-1", kind="dua")
            self.write(folder, "quran.json", "quran-1", kind="quran")
            self.assertEqual(choose_manifest(folder, "dua", rotation_key="day-1"), dua)


if __name__ == "__main__":
    unittest.main()
