import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import prepare_quran_review_batch_audio as module


class FakeArchive:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def open(self, member):
        return io.BytesIO(b"fake-mp3")


class QuranBatchAudioTests(unittest.TestCase):
    def test_prepares_distinct_surahs_without_approving_or_publishing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            batch = {
                "batch_status": "review_candidates_only",
                "rendering_allowed": False,
                "auto_publish": False,
                "passages": [
                    {"candidate_id": "s1", "surah_number": 1, "verses": [{"ayah": 1}, {"ayah": 2}]},
                    {"candidate_id": "s2", "surah_number": 2, "verses": [{"ayah": 1}, {"ayah": 2}]},
                    {"candidate_id": "s3", "surah_number": 3, "verses": [{"ayah": 1}, {"ayah": 2}, {"ayah": 3}]},
                ],
            }
            inventory = {
                "mapped_verse_count": 6236,
                "verses": {f"{s}:{a}": f"{s}-{a}.mp3" for s in (1, 2, 3) for a in (1, 2, 3)},
            }
            batch_path, inventory_path = root / "batch.json", root / "inventory.json"
            batch_path.write_text(json.dumps(batch), encoding="utf-8")
            inventory_path.write_text(json.dumps(inventory), encoding="utf-8")

            def fake_run(command, **kwargs):
                Path(command[-1]).write_bytes(b"combined")
                return None

            with patch.object(module, "RemoteZip", return_value=FakeArchive()), \
                 patch.object(module, "probe", side_effect=[12.0, 14.0, 26.0, 13.0, 15.0, 28.0, 40.0, 30.0, 40.0]), \
                 patch.object(module.subprocess, "run", side_effect=fake_run):
                report = module.prepare_batch(batch_path, inventory_path, root / "out")

            self.assertEqual(report["audio_prepared_count"], 3)
            partial = next(item for item in report["items"] if item["candidate_id"] == "s3")
            self.assertTrue(partial["status"].startswith("audio_prepared"))
            self.assertEqual(partial["requested_verses"], [1, 2])
            self.assertEqual(partial["selected_verses"], [1])
            self.assertEqual(partial["duration_seconds"], 40.0)
            self.assertEqual(report["distinct_surah_count"], 3)
            self.assertFalse(report["rendering_allowed"])
            self.assertFalse(report["telegram_delivery"])
            self.assertFalse(report["auto_publish"])
            self.assertTrue(all(not item.get("audio_approved", True) for item in report["items"]))

    def test_rejects_non_review_only_batch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            batch_path, inventory_path = root / "batch.json", root / "inventory.json"
            batch_path.write_text(json.dumps({"batch_status": "approved", "rendering_allowed": True}))
            inventory_path.write_text(json.dumps({"mapped_verse_count": 6236, "verses": {}}))
            with self.assertRaisesRegex(ValueError, "review-only"):
                module.prepare_batch(batch_path, inventory_path, root / "out")


if __name__ == "__main__":
    unittest.main()
