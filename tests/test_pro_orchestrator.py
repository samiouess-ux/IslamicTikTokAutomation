"""Tests for isolated dua/dhikr Pro preflight and repeat protection."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from pro_orchestrator import build_plan


class ProOrchestratorTests(unittest.TestCase):
    def write_manifest(self, folder: Path, name: str, manifest_id: str, item_id: str,
                       content_type: str = "dua") -> Path:
        data = {
            "id": manifest_id,
            "rotation_approved": True,
            "content_type": content_type,
            "source": {"collection": "reviewed"},
            "items": [{
                "id": item_id, "kind": "quranic_dua",
                "arabic": "رَبَّنَا آتِنَا فِي الدُّنْيَا حَسَنَةً",
                "source_name": "Quran", "source_url": "https://example.org/quran",
                "source_reference": "Al-Baqarah 2:201",
                "verification_status": "verified", "human_reviewed": True,
            }],
            "audio": {"kind": "silent", "music_allowed": False, "duration_seconds": 12},
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

    def test_builds_dua_plan_and_preserves_item_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            manifest = self.write_manifest(folder, "dua.json", "dua-manifest-1", "dua-item-1")
            plan = build_plan(folder, {"content": []}, "dua", "2026-11-06", 1)
            self.assertEqual(plan[0]["manifest"], str(manifest))
            self.assertEqual(plan[0]["item_id"], "dua-item-1")

    def test_recent_manifest_is_not_repeated(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            self.write_manifest(folder, "dua.json", "already-used", "item-1")
            with self.assertRaisesRegex(FileNotFoundError, "refusing to repeat"):
                build_plan(folder, {"content": ["already-used"]}, "dua", "2026-11-06", 1)

    def test_rejects_wrong_pro_content_type(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "dua or dhikr"):
                build_plan(Path(tmp), {"content": []}, "quran", "2026-11-06", 1)

    def test_rejects_multi_item_video_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            path = self.write_manifest(folder, "dua.json", "dua-manifest-1", "item-1")
            data = json.loads(path.read_text(encoding="utf-8"))
            data["items"].append(dict(data["items"][0], id="item-2"))
            path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            with self.assertRaisesRegex(SystemExit, "exactly one item"):
                build_plan(folder, {"content": []}, "dua", "2026-11-06", 1)


if __name__ == "__main__":
    unittest.main()
