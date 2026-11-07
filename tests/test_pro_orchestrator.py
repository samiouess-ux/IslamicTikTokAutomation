"""Tests for isolated dua/dhikr Pro preflight and repeat protection."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from pro_orchestrator import build_plan, build_preview_plan, read_json


class ProOrchestratorTests(unittest.TestCase):
    def write_manifest(self, folder: Path, name: str, manifest_id: str, item_id: str,
                       content_type: str = "dua") -> Path:
        data = {
            "id": manifest_id,
            "rotation_approved": True,
            "content_type": content_type,
            "source": {"collection": "reviewed"},
            "items": [{
                "id": item_id, "kind": "quranic_dua", "duration_seconds": 12,
                "arabic": "رَبَّنَا آتِنَا فِي الدُّنْيَا حَسَنَةً",
                "source_name": "Quran", "source_url": "https://example.org/quran",
                "source_reference": "Al-Baqarah 2:201",
                "verification_status": "verified", "human_reviewed": True,
            }],
            "audio": {"kind": "silent", "music_allowed": False},
            "visual": {"template": "ornate_gold_classic", "background_candidate": {
                "source_url": "https://example.org/source",
                "direct_video_url": "https://example.org/background.mp4",
                "approved": True, "user_approved": True,
            }},
            "publishing": {"approval_required": True, "auto_publish": False},
        }
        path = folder / name
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        return path

    def test_read_json_reports_invalid_utf8_as_controlled_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "invalid.json"
            path.write_bytes(b'{"broken":\xff}')
            with self.assertRaisesRegex(SystemExit, "Cannot read JSON file"):
                read_json(path)

    def test_builds_dua_plan_and_preserves_item_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            manifest = self.write_manifest(folder, "dua.json", "dua-manifest-1", "dua-item-1")
            plan = build_plan(folder, {"content": []}, "dua", "2026-11-06", 1)
            self.assertEqual(plan[0]["manifest"], str(manifest))
            self.assertEqual(plan[0]["item_ids"], ["dua-item-1"])

    def test_recent_manifest_is_not_repeated(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            self.write_manifest(folder, "dua.json", "already-used", "item-1")
            with self.assertRaisesRegex(FileNotFoundError, "refusing to repeat"):
                build_plan(folder, {"content": ["already-used"]}, "dua", "2026-11-06", 1)

    def test_candidate_preview_is_separate_from_rotation_and_production(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            path = self.write_manifest(folder, "candidate.json", "candidate-1", "candidate-item")
            data = json.loads(path.read_text(encoding="utf-8"))
            data["lifecycle_status"] = "candidate_preview"
            data["preview_only"] = True
            data["rotation_approved"] = False
            data["items"][0]["human_reviewed"] = False
            path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            plan = build_preview_plan(path)
            self.assertTrue(plan["preview_only"])
            self.assertEqual(plan["lifecycle_status"], "candidate_preview")
            self.assertEqual(plan["content_id"], "candidate-1")
            with self.assertRaisesRegex(FileNotFoundError, "No eligible non-recent dua manifest"):
                build_plan(folder, {"content": []}, "dua", "2026-11-06", 1)

    def test_candidate_preview_rejects_rotation_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            path = self.write_manifest(folder, "candidate.json", "candidate-1", "candidate-item")
            data = json.loads(path.read_text(encoding="utf-8"))
            data["lifecycle_status"] = "candidate_preview"
            data["preview_only"] = True
            data["items"][0]["human_reviewed"] = False
            path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            with self.assertRaisesRegex(SystemExit, "never be rotation-approved"):
                build_preview_plan(path)

    def test_production_plan_rejects_unsafe_output_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            self.write_manifest(folder, "dua.json", "../escape", "item-1")
            with self.assertRaisesRegex(SystemExit, "safe filename component"):
                build_plan(folder, {"content": []}, "dua", "2026-11-07", 1)

    def test_candidate_preview_rejects_unsafe_output_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            path = self.write_manifest(folder, "candidate.json", "../escape", "candidate-item")
            data = json.loads(path.read_text(encoding="utf-8"))
            data["lifecycle_status"] = "candidate_preview"
            data["preview_only"] = True
            data["rotation_approved"] = False
            data["items"][0]["human_reviewed"] = False
            path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            with self.assertRaisesRegex(SystemExit, "safe filename component"):
                build_preview_plan(path)

    def test_rejects_non_string_rotation_content_type(self):
        for content_type in ([], {}, 7, True):
            with self.subTest(content_type=content_type), self.assertRaisesRegex(ValueError, "dua or dhikr"):
                build_plan(Path("."), {"content": []}, content_type, "2026-11-07", 1)

    def test_rejects_wrong_pro_content_type(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "dua or dhikr"):
                build_plan(Path(tmp), {"content": []}, "quran", "2026-11-06", 1)

    def test_batch_rejects_reusing_the_same_background_video(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            first = self.write_manifest(folder, "a.json", "dua-a", "item-a")
            second = self.write_manifest(folder, "b.json", "dua-b", "item-b")
            data = json.loads(second.read_text(encoding="utf-8"))
            first_data = json.loads(first.read_text(encoding="utf-8"))
            data["visual"]["background_candidate"]["direct_video_url"] = first_data["visual"]["background_candidate"]["direct_video_url"]
            second.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            with self.assertRaisesRegex(SystemExit, "cannot reuse the same exact background video"):
                build_plan(folder, {"content": []}, "dua", "2026-11-07", 2)

    def test_batch_accepts_distinct_background_videos(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            self.write_manifest(folder, "a.json", "dua-a", "item-a")
            second = self.write_manifest(folder, "b.json", "dua-b", "item-b")
            data = json.loads(second.read_text(encoding="utf-8"))
            data["visual"]["background_candidate"]["direct_video_url"] = "https://example.org/other-background.mp4"
            second.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            plan = build_plan(folder, {"content": []}, "dua", "2026-11-07", 2)
            self.assertEqual(len(plan), 2)

    def test_supports_multiple_sourced_items_in_one_video(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            path = self.write_manifest(folder, "dua.json", "dua-manifest-1", "item-1")
            data = json.loads(path.read_text(encoding="utf-8"))
            data["items"].append(dict(data["items"][0], id="item-2"))
            path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            plan = build_plan(folder, {"content": []}, "dua", "2026-11-06", 1)
            self.assertEqual(plan[0]["item_ids"], ["item-1", "item-2"])


    def test_rotation_plan_rejects_non_finite_item_durations(self):
        for duration in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(duration=duration), tempfile.TemporaryDirectory() as tmp:
                folder = Path(tmp)
                path = self.write_manifest(folder, "dua.json", "dua-manifest", "item-1")
                data = json.loads(path.read_text(encoding="utf-8"))
                data["items"][0]["duration_seconds"] = duration
                path.write_text(json.dumps(data), encoding="utf-8")
                with self.assertRaisesRegex(SystemExit, "positive duration_seconds"):
                    build_plan(folder, {"content": []}, "dua", "2026-11-07", 1)

    def test_candidate_preview_rejects_non_finite_item_durations(self):
        for duration in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(duration=duration), tempfile.TemporaryDirectory() as tmp:
                folder = Path(tmp)
                path = self.write_manifest(folder, "candidate.json", "candidate-1", "item-1")
                data = json.loads(path.read_text(encoding="utf-8"))
                data["lifecycle_status"] = "candidate_preview"
                data["preview_only"] = True
                data["rotation_approved"] = False
                data["items"][0]["human_reviewed"] = False
                data["items"][0]["duration_seconds"] = duration
                path.write_text(json.dumps(data), encoding="utf-8")
                with self.assertRaisesRegex(SystemExit, "positive duration_seconds"):
                    build_preview_plan(path)



    def test_candidate_preview_rejects_non_string_content_type(self):
        for content_type in ([], {}, 7, True):
            with self.subTest(content_type=content_type), tempfile.TemporaryDirectory() as tmp:
                folder = Path(tmp)
                path = self.write_manifest(folder, "candidate.json", "candidate-1", "item-1")
                data = json.loads(path.read_text(encoding="utf-8"))
                data["content_type"] = content_type
                data["lifecycle_status"] = "candidate_preview"
                data["preview_only"] = True
                data["rotation_approved"] = False
                data["items"][0]["human_reviewed"] = False
                path.write_text(json.dumps(data), encoding="utf-8")
                with self.assertRaisesRegex(SystemExit, "must be dua or dhikr"):
                    build_preview_plan(path)


if __name__ == "__main__":
    unittest.main()
