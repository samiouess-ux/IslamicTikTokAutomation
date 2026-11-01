import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from telegram_request_state import load_state, is_duplicate, record_update, save_state


class TelegramRequestStateTests(unittest.TestCase):
    def test_missing_state_starts_empty(self):
        with tempfile.TemporaryDirectory() as directory:
            state = load_state(Path(directory) / "state.json")
        self.assertEqual(state, {"schema_version": 1, "last_update_id": 0, "processed_update_ids": []})

    def test_records_and_detects_duplicate_update(self):
        state = {"schema_version": 1, "last_update_id": 0, "processed_update_ids": []}
        state = record_update(state, 101)
        self.assertTrue(is_duplicate(state, 101))
        self.assertTrue(is_duplicate(state, 100))
        self.assertFalse(is_duplicate(state, 102))

    def test_state_round_trip_is_atomic_json(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nested" / "state.json"
            state = record_update(load_state(path), 77)
            save_state(state, path)
            self.assertEqual(load_state(path), state)
            self.assertTrue(path.read_bytes().endswith(b"\n"))
            self.assertFalse(path.with_suffix(".json.tmp").exists())

    def test_corrupt_state_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            path.write_text("{broken", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unreadable"):
                load_state(path)

    def test_invalid_update_id_rejected(self):
        state = load_state(Path("/nonexistent/telegram-state-test.json"))
        with self.assertRaises(ValueError):
            record_update(state, -1)


if __name__ == "__main__":
    unittest.main()
