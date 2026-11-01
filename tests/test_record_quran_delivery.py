import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from record_quran_delivery import EMPTY, record_delivery, save_history


class DeliveryHistoryTests(unittest.TestCase):
    def candidate(self):
        return {
            "candidate_id": "quran_s011_001_123",
            "surah_number": 11,
            "verses": [
                {"ayah": n, "reference": f"11:{n}"}
                for n in range(1, 124)
            ],
        }

    def test_records_only_selected_prefix_not_entire_candidate(self):
        history = {"schema_version": 1, "ayah_references": [], "deliveries": []}
        result = record_delivery(history, self.candidate(), [1, 2])
        self.assertEqual(result["ayah_references"], ["11:1", "11:2"])
        self.assertEqual(result["deliveries"][0]["selected_verses"], [1, 2])
        self.assertEqual(len(result["deliveries"]), 1)

    def test_rejects_non_prefix_or_non_contiguous_selection(self):
        history = {"schema_version": 1, "ayah_references": [], "deliveries": []}
        with self.assertRaisesRegex(ValueError, "contiguous prefix"):
            record_delivery(history, self.candidate(), [1, 3])

    def test_rejects_duplicate_ayah(self):
        item = {"candidate_id": "x", "surah_number": 1, "verses": [{"ayah": 1, "reference": "1:1"}]}
        history = {"schema_version": 1, "ayah_references": ["1:1"], "deliveries": []}
        with self.assertRaises(ValueError):
            record_delivery(history, item, [1])

    def test_saved_history_is_valid_json_with_real_newline(self):
        history = {"schema_version": 1, "ayah_references": ["1:1"], "deliveries": []}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nested" / "history.json"
            save_history(history, path)
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), history)
            self.assertTrue(path.read_bytes().endswith(b"\n"))


if __name__ == "__main__":
    unittest.main()
