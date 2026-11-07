"""Tests for deterministic reviewed-content rotation."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock
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

    def test_skips_manifests_with_invalid_utf8(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "invalid-utf8.json").write_bytes(b'{"id":"bad","content_type":"quran",\xff}')
            valid = self.write(folder, "valid.json", "valid")
            self.assertEqual(choose_manifest(folder, "quran", rotation_key="utf8-check"), valid)

    def test_batch_fails_closed_if_selected_file_becomes_invalid_utf8(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            self.write(folder, "candidate.json", "candidate")
            import content_rotation
            original = content_rotation.choose_manifest

            def select_then_corrupt(*args, **kwargs):
                path = original(*args, **kwargs)
                path.write_bytes(b'{"id":"candidate",\xff}')
                return path

            with mock.patch("content_rotation.choose_manifest", side_effect=select_then_corrupt):
                with self.assertRaisesRegex(ValueError, "changed or became unreadable"):
                    choose_manifests(folder, "quran", count=1, rotation_key="race-utf8")

    def test_skips_manifest_with_non_object_publishing_field(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "bad.json").write_text(json.dumps({
                "id": "bad", "content_type": "quran", "rotation_approved": True,
                "publishing": ["approval_required", True],
            }), encoding="utf-8")
            valid = self.write(folder, "valid.json", "valid")
            self.assertEqual(choose_manifest(folder, "quran", rotation_key="publishing-check"), valid)

    def test_batch_fails_closed_if_selected_file_becomes_invalid_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            selected = self.write(folder, "candidate.json", "candidate")
            import content_rotation
            original = content_rotation.choose_manifest

            def select_then_corrupt(*args, **kwargs):
                path = original(*args, **kwargs)
                path.write_text("{ invalid json", encoding="utf-8")
                return path

            with mock.patch("content_rotation.choose_manifest", side_effect=select_then_corrupt):
                with self.assertRaisesRegex(ValueError, "changed or became unreadable"):
                    choose_manifests(folder, "quran", count=1, rotation_key="race-json")

    def test_batch_fails_closed_if_selected_manifest_loses_its_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            selected = self.write(folder, "candidate.json", "candidate")
            import content_rotation
            original = content_rotation.choose_manifest

            def select_then_remove_id(*args, **kwargs):
                path = original(*args, **kwargs)
                data = json.loads(path.read_text(encoding="utf-8"))
                del data["id"]
                path.write_text(json.dumps(data), encoding="utf-8")
                return path

            with mock.patch("content_rotation.choose_manifest", side_effect=select_then_remove_id):
                with self.assertRaisesRegex(ValueError, "no longer eligible"):
                    choose_manifests(folder, "quran", count=1, rotation_key="race-id")

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

    def test_rejects_malformed_rotation_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            self.write(folder, "a.json", "one")
            for invalid_type in ([], {}, 7, True):
                with self.subTest(content_type=invalid_type), self.assertRaisesRegex(ValueError, "Unsupported content type"):
                    choose_manifest(folder, invalid_type)
            for recent in ([["nested"]], [{"id": "one"}], [None]):
                with self.subTest(recent=recent), self.assertRaisesRegex(ValueError, "recent_ids"):
                    choose_manifest(folder, "quran", recent)
            with self.assertRaisesRegex(ValueError, "rotation_key"):
                choose_manifest(folder, "quran", rotation_key=[])

    def test_recent_ids_reject_non_iterables_and_scalar_strings(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            self.write(folder, "a.json", "one")
            for invalid_recent in (None, 7, {}, "single-id", b"bytes"):
                with self.subTest(recent_ids=invalid_recent):
                    with self.assertRaisesRegex(ValueError, "recent_ids"):
                        choose_manifest(folder, "quran", recent_ids=invalid_recent)
                    with self.assertRaisesRegex(ValueError, "recent_ids"):
                        choose_manifests(folder, "quran", count=1, recent_ids=invalid_recent)

    def test_batch_count_rejects_booleans(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            self.write(folder, "a.json", "one")
            for invalid_count in (True, False):
                with self.subTest(count=invalid_count):
                    with self.assertRaisesRegex(ValueError, "positive integer"):
                        choose_manifests(
                            folder, "quran", count=invalid_count,
                            rotation_key="boolean-count",
                        )

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
