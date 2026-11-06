"""Offline tests for isolated Pro preview ledger identity and transitions."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from pro_preview_send_ledger import load_ledger, reserve, transition, validate_ledger


class PreviewLedgerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "preview.json"

    def tearDown(self):
        self.tmp.cleanup()

    def reserve_one(self):
        return reserve(self.path, "candidate-001", "dua", "a" * 64, "b" * 64, "run-1")

    def test_empty_ledger_and_reservation_are_versioned(self):
        self.assertEqual(load_ledger(self.path), {"version": 1, "entries": {}})
        entry = self.reserve_one()
        self.assertEqual(entry["state"], "reserved")
        self.assertIsNone(entry["telegram_message_id"])

    def test_duplicate_id_blocks_even_when_hashes_match(self):
        self.reserve_one()
        with self.assertRaisesRegex(ValueError, "refusing duplicate"):
            self.reserve_one()

    def test_changed_hash_under_same_id_is_identity_conflict(self):
        self.reserve_one()
        with self.assertRaisesRegex(ValueError, "identity conflict"):
            reserve(self.path, "candidate-001", "dua", "c" * 64, "b" * 64, "run-2")

    def test_rejects_bad_schema_and_hash(self):
        self.path.write_text('{"version":2,"entries":{}}', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Unsupported"):
            load_ledger(self.path)
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            validate_ledger({"version": 1, "entries": {
                "candidate-001": {"candidate_id":"candidate-001","content_type":"dua",
                "manifest_sha256":"bad","video_sha256":"b"*64,"workflow_run_id":"run",
                "state":"reserved","created_at":"now","updated_at":"now","telegram_message_id":None}
            }})

    def test_delivered_requires_positive_non_boolean_message_id(self):
        self.reserve_one()
        for bad in (True, 0, -1, "77"):
            with self.assertRaisesRegex(ValueError, "positive integer"):
                transition(self.path, "candidate-001", "delivered", bad)
        self.assertEqual(transition(self.path, "candidate-001", "delivered", 77)["state"], "delivered")

    def test_ambiguous_blocks_duplicate_and_can_only_be_resolved_with_receipt(self):
        self.reserve_one()
        transition(self.path, "candidate-001", "uncertain")
        with self.assertRaisesRegex(ValueError, "refusing duplicate"):
            self.reserve_one()
        self.assertEqual(transition(self.path, "candidate-001", "delivered", 88)["telegram_message_id"], 88)

    def test_rejects_unsafe_candidate_id(self):
        with self.assertRaisesRegex(ValueError, "safe"):
            reserve(self.path, "../escape", "dua", "a"*64, "b"*64, "run")


if __name__ == "__main__":
    unittest.main()
