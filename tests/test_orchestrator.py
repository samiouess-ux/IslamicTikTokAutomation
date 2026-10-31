"""Tests for the review-only daily orchestrator."""
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
    def test_fails_closed_when_any_required_category_is_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "quran.json").write_text(json.dumps({
                "id": "q1", "content_type": "quran", "rotation_approved": True,
                "publishing": {"approval_required": True, "auto_publish": False}
            }), encoding="utf-8")
            with patch("orchestrator.validate_content_manifest"):
                with self.assertRaisesRegex(FileNotFoundError, "dua"):
                    build_plan(folder, {"content": []}, "test-day")

    def test_all_three_types_are_selected_and_validated_before_plan_returns(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            manifests = {}
            for kind in ("quran", "dua", "dhikr"):
                path = folder / f"{kind}.json"
                path.write_text(json.dumps({
                    "id": f"{kind}-1",
                    "content_type": kind,
                    "publishing": {"approval_required": True, "auto_publish": False},
                }), encoding="utf-8")
                manifests[kind] = path
            def choose(_folder, kind, _recent, _key):
                return manifests[kind]
            with patch("orchestrator.choose_manifest", side_effect=choose), \
                 patch("orchestrator.validate_content_manifest") as validate:
                plan = build_plan(folder, {"content": []}, "test-day")
            self.assertEqual([item["content_type"] for item in plan],
                             ["quran", "dua", "dhikr"])
            self.assertEqual(validate.call_count, 3)
            self.assertEqual(len({item["content_id"] for item in plan}), 3)

    def test_manifest_must_explicitly_match_requested_category(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            path = folder / "quran.json"
            path.write_text(json.dumps({
                "id": "q1",
                "publishing": {"approval_required": True, "auto_publish": False},
            }), encoding="utf-8")
            with patch("orchestrator.choose_manifest", return_value=path), \
                 patch("orchestrator.validate_content_manifest"):
                with self.assertRaisesRegex(SystemExit, "must explicitly declare"):
                    build_plan(folder, {"content": []}, "test-day")

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
