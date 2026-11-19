import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from quran_visual_history import load_history, recent_usage, record_visual_delivery, save_history


class QuranVisualHistoryTests(unittest.TestCase):
    def report(self):
        return {"preview_count": 1, "items": [{
            "candidate_id": "candidate-001", "cover_template_id": "cover-gold",
            "background_sequence": [
                {"id": "mountain-01", "tags": ["mountains", "sunset"], "background_type": "photo"},
                {"id": "mosque-02", "tags": ["mosque", "architecture"], "background_type": "moving_video"},
            ],
        }]}

    def test_record_requires_confirmed_telegram_delivery(self):
        with self.assertRaisesRegex(ValueError, "only be recorded after confirmed Telegram"):
            record_visual_delivery({"schema_version": 1, "deliveries": []}, self.report())

    def test_record_persists_asset_ids_categories_and_cover(self):
        history = record_visual_delivery({"schema_version": 1, "deliveries": []}, self.report(), telegram_confirmed=True)
        entry = history["deliveries"][0]
        self.assertEqual(entry["candidate_id"], "candidate-001")
        self.assertEqual([x["id"] for x in entry["backgrounds"]], ["mountain-01", "mosque-02"])
        self.assertEqual(entry["backgrounds"][0]["categories"], ["mountains", "sunset"])
        self.assertEqual(entry["cover_template_id"], "cover-gold")

    def test_record_is_idempotent_for_same_candidate_and_visuals(self):
        history = record_visual_delivery({"schema_version": 1, "deliveries": []}, self.report(), telegram_confirmed=True)
        record_visual_delivery(history, self.report(), telegram_confirmed=True)
        self.assertEqual(len(history["deliveries"]), 1)

    def test_same_candidate_with_different_visuals_is_rejected(self):
        history = record_visual_delivery({"schema_version": 1, "deliveries": []}, self.report(), telegram_confirmed=True)
        changed = self.report()
        changed["items"][0]["cover_template_id"] = "cover-blue"
        with self.assertRaisesRegex(ValueError, "different visual assets"):
            record_visual_delivery(history, changed, telegram_confirmed=True)

    def test_recent_usage_uses_bounded_windows(self):
        history = {"schema_version": 1, "deliveries": []}
        for index in range(8):
            history["deliveries"].append({
                "candidate_id": f"candidate-{index}",
                "backgrounds": [{"id": f"bg-{index}", "categories": [f"category-{index}"]}],
                "cover_template_id": f"cover-{index}",
            })
        ids, categories, covers = recent_usage(history, background_window=3, cover_window=2)
        self.assertEqual(ids, {"bg-5", "bg-6", "bg-7"})
        self.assertEqual(categories, {"category-5", "category-6", "category-7"})
        self.assertEqual(covers, {"cover-6", "cover-7"})

    def test_history_round_trips_and_rejects_malformed_schema(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "visual-history.json"
            history = record_visual_delivery({"schema_version": 1, "deliveries": []}, self.report(), telegram_confirmed=True)
            save_history(history, path)
            self.assertEqual(load_history(path), history)
            path.write_text('{"schema_version":2,"deliveries":[]}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "malformed or unsupported"):
                load_history(path)


if __name__ == "__main__":
    unittest.main()
