import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from quran_delivery_attempt import guard_no_pending, reserve_attempt, finalize_attempt


class QuranDeliveryAttemptTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.pending = self.root / "pending.json"
        self.history = self.root / "history.json"
        self.batch = self.root / "batch.json"
        self.audio = self.root / "audio.json"
        self.preview = self.root / "preview.json"
        self.candidate_id = "quran_s011_001_003"
        passage = {
            "candidate_id": self.candidate_id,
            "surah_number": 11,
            "verses": [{"ayah": n, "reference": f"11:{n}"} for n in range(1, 4)],
        }
        self.batch.write_text(json.dumps({"passages": [passage]}), encoding="utf-8")
        self.audio.write_text(json.dumps({"items": [{
            "candidate_id": self.candidate_id,
            "status": "audio_prepared",
            "selected_verses": [1, 2],
        }]}), encoding="utf-8")
        self.preview.write_text(json.dumps({
            "preview_count": 1,
            "auto_publish": False,
            "items": [{"candidate_id": self.candidate_id, "file": "preview.mp4"}],
        }), encoding="utf-8")
        self.history.write_text(json.dumps({
            "schema_version": 1, "ayah_references": [], "deliveries": []
        }), encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def reserve(self):
        return reserve_attempt(self.pending, self.history, self.batch, self.audio, self.preview)

    def test_reserves_exact_selected_ayahs_before_send(self):
        pending = self.reserve()
        self.assertEqual(pending["ayah_references"], ["11:1", "11:2"])
        self.assertTrue(self.pending.exists())
        self.assertEqual(json.loads(self.history.read_text())["ayah_references"], [])

    def test_existing_pending_attempt_blocks_another_send(self):
        self.reserve()
        with self.assertRaisesRegex(RuntimeError, "Unresolved Telegram"):
            guard_no_pending(self.pending)
        with self.assertRaisesRegex(RuntimeError, "Unresolved Telegram"):
            self.reserve()

    def test_confirmed_finalize_records_history_and_clears_pending(self):
        self.reserve()
        result = finalize_attempt(
            self.pending, self.history, self.batch, self.audio, self.candidate_id
        )
        self.assertEqual(result["ayah_references"], ["11:1", "11:2"])
        self.assertFalse(self.pending.exists())

    def test_finalize_wrong_candidate_keeps_pending(self):
        self.reserve()
        with self.assertRaisesRegex(RuntimeError, "No matching pending"):
            finalize_attempt(self.pending, self.history, self.batch, self.audio, "wrong")
        self.assertTrue(self.pending.exists())

    def test_reservation_rejects_already_delivered_ayahs(self):
        self.history.write_text(json.dumps({
            "schema_version": 1, "ayah_references": ["11:1"], "deliveries": []
        }), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "already present"):
            self.reserve()
        self.assertFalse(self.pending.exists())


if __name__ == "__main__":
    unittest.main()
