"""Tests for the Quran-only review orchestrator."""
import json
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from orchestrator import build_plan, load_history


class OrchestratorTests(unittest.TestCase):
    def test_selects_three_distinct_quran_manifests_without_dua_or_dhikr(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            manifests = []
            for index in range(3):
                path = folder / f"quran-{index}.json"
                path.write_text(json.dumps({
                    "id": f"quran-{index}",
                    "content_type": "quran",
                    "publishing": {"approval_required": True, "auto_publish": False},
                }), encoding="utf-8")
                manifests.append(path)

            def choose_many(_folder, kind, count, _recent, _key):
                self.assertEqual(kind, "quran")
                self.assertEqual(count, 3)
                return manifests

            with patch("orchestrator.choose_manifests", side_effect=choose_many), \\
                 patch("orchestrator.validate_content_manifest") as validate:
                plan = build_plan(folder, {"content": []}, "test-day")

            self.assertEqual([item["content_type"] for item in plan],
                             ["quran", "quran", "quran"])
            self.assertEqual(validate.call_count, 3)
            self.assertEqual(len({item["content_id"] for item in plan}), 3)

    def test_missing_quran_manifest_blocks_incomplete_three_video_batch(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            with patch("orchestrator.choose_manifests",
                       side_effect=FileNotFoundError("only one Quran manifest")):
                with self.assertRaisesRegex(FileNotFoundError, "only one Quran"):
                    build_plan(folder, {"content": []}, "test-day")

    def test_manifest_must_explicitly_match_quran_category(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            path = folder / "quran.json"
            path.write_text(json.dumps({
                "id": "q1",
                "publishing": {"approval_required": True, "auto_publish": False},
            }), encoding="utf-8")
            with patch("orchestrator.choose_manifests", return_value=[path]), \\
                 patch("orchestrator.validate_content_manifest"):
                with self.assertRaisesRegex(SystemExit, "must explicitly declare"):
                    build_plan(folder, {"content": []}, "test-day", video_count=1)

    def test_missing_history_starts_empty_without_creating_a_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "history.json"
            history = load_history(path)
            self.assertEqual(history, {"content": []})
            self.assertFalse(path.exists())

    def test_invalid_history_content_field_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "history.json"
            path.write_text('{"content":"not-a-list"}', encoding="utf-8")
            with self.assertRaisesRegex(SystemExit, "must be a list"):
                load_history(path)


if __name__ == "__main__":
    unittest.main()
