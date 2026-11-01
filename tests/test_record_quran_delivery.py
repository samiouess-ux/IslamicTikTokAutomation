import json, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from record_quran_delivery import EMPTY, record_delivery, save_history

class DeliveryHistoryTests(unittest.TestCase):
    def test_records_confirmed_candidate(self):
        item = {"candidate_id":"quran_s001_001_002", "surah_number":1, "verses":[{"reference":"1:1"},{"reference":"1:2"}]}
        history = {"schema_version":1, "ayah_references":[], "deliveries":[]}
        result = record_delivery(history, item)
        self.assertEqual(result["ayah_references"], ["1:1", "1:2"])
        self.assertEqual(len(result["deliveries"]), 1)

    def test_rejects_duplicate_ayah(self):
        item = {"candidate_id":"x", "surah_number":1, "verses":[{"reference":"1:1"}]}
        history = {"schema_version":1, "ayah_references":["1:1"], "deliveries":[]}
        with self.assertRaises(ValueError): record_delivery(history, item)

    def test_saved_history_is_valid_json_with_real_newline(self):
        history = {"schema_version":1, "ayah_references":["1:1"], "deliveries":[]}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nested" / "history.json"
            save_history(history, path)
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), history)
            self.assertTrue(path.read_bytes().endswith(b"\n"))

if __name__ == "__main__": unittest.main()
