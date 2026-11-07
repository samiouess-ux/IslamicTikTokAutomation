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


    def test_skips_valid_json_that_is_not_an_object(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "a-list.json").write_text('["not", "an", "object"]', encoding="utf-8")
            (folder / "b-null.json").write_text('null', encoding="utf-8")
            valid = self.write(folder, "valid.json", "valid")
            self.assertEqual(choose_manifest(folder, "quran", rotation_key="shape-check"), valid)

    def test_skips_manifest_with_non_object_publishing_field(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "bad.json").write_text(json.dumps({
                "id": "bad", "content_type": "quran", "rotation_approved": True,
                "publishing": ["approval_required", True],
            }), encoding="utf-8")
            valid = self.write(folder, "valid.json", "valid")
            self.assertEqual(choose_manifest(folder, "quran", rotation_key="publishing-check"), valid)

    def test_selects_three_distinct_approved_manifests(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            expected = {
                self.write(folder, "a.json", "one"),
                self.write(folder, "b.json", "two"),
                self.write(folder, "c.json", "three"),
            }
            selected = choose_manifests(
                folder, "quran", count=3, rotation_key="daily-batch"
            )
            self.assertEqual(len(selected), 3)
            self.assertEqual(len({p.name for p in selected}), 3)
            self.assertEqual(set(selected), expected)

    def test_batch_fails_closed_when_three_distinct_items_are_unavailable(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            self.write(folder, "a.json", "one")
            self.write(folder, "b.json", "two")
            with self.assertRaisesRegex(FileNotFoundError, "complete batch of 3"):
                choose_manifests(
                    folder, "quran", count=3, rotation_key="daily-batch"
                )


if __name__ == "__main__":
    unittest.main()
