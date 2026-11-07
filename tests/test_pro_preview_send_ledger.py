"""Offline tests for isolated Pro preview ledger identity and transitions."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from pro_preview_send_ledger import load_ledger, reserve, save_ledger, transition, validate_ledger


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

    def test_invalid_utf8_ledger_is_reported_as_safe_validation_error(self):
        self.path.write_bytes(b'\\xff\\xfe{')
        with self.assertRaisesRegex(ValueError, "Cannot safely read Pro preview ledger") as caught:
            load_ledger(self.path)
        self.assertIsNone(caught.exception.__cause__)

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
        with self.assertRaisesRegex(ValueError, "recovered_receipt"):
            transition(self.path, "candidate-001", "delivered", 88)
        self.assertEqual(transition(self.path, "candidate-001", "delivered", 88, recovered_receipt=True)["telegram_message_id"], 88)

    def test_ledger_rejects_unhashable_enum_values(self):
        base = {
            "candidate_id": "candidate-001", "content_type": "dua",
            "manifest_sha256": "a" * 64, "video_sha256": "b" * 64,
            "workflow_run_id": "run-1", "state": "reserved",
            "created_at": "now", "updated_at": "now",
            "telegram_message_id": None,
        }
        for field, invalid in (("content_type", []), ("content_type", {}),
                               ("state", []), ("state", {})):
            with self.subTest(field=field, invalid=invalid):
                entry = dict(base)
                entry[field] = invalid
                with self.assertRaisesRegex(ValueError, "unsupported"):
                    validate_ledger({"version": 1, "entries": {"candidate-001": entry}})

    def test_transition_rejects_malformed_candidate_ids(self):
        self.reserve_one()
        for bad in ([], {}, 12, True, ""):
            with self.subTest(candidate_id=bad):
                with self.assertRaisesRegex(ValueError, "safe"):
                    transition(self.path, bad, "delivered", 99)

    def test_refuses_symlinked_ledger_file_for_read_and_write(self):
        target = self.path.with_name("outside-ledger.json")
        target.write_text('{"version":1,"entries":{}}', encoding="utf-8")
        try:
            self.path.symlink_to(target)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks are unavailable on this platform.")
        with self.assertRaisesRegex(ValueError, "must not be a symlink"):
            load_ledger(self.path)
        with self.assertRaisesRegex(ValueError, "must not be symlinks"):
            save_ledger(self.path, {"version": 1, "entries": {}})
        self.assertEqual(target.read_text(encoding="utf-8"), '{"version":1,"entries":{}}')

    def test_refuses_symlinked_parent_directory_before_creating_lock(self):
        outside = Path(self.tmp.name) / "outside-dir"
        outside.mkdir()
        linked_parent = Path(self.tmp.name) / "linked-data"
        try:
            linked_parent.symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks are unavailable on this platform.")
        linked_ledger = linked_parent / "preview.json"
        with self.assertRaisesRegex(ValueError, "must not contain symlinks"):
            reserve(linked_ledger, "candidate-001", "dua", "a" * 64, "b" * 64, "run-1")
        self.assertEqual(list(outside.iterdir()), [])

    def test_refuses_symlinked_lock_file(self):
        target = self.path.with_name("outside.lock")
        target.write_text("untouched", encoding="utf-8")
        lock = self.path.with_name(self.path.name + ".lock")
        try:
            lock.symlink_to(target)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks are unavailable on this platform.")
        with self.assertRaisesRegex(ValueError, "lock file must not be a symlink"):
            self.reserve_one()
        self.assertEqual(target.read_text(encoding="utf-8"), "untouched")
        self.assertFalse(self.path.exists())

    def test_rejects_unsafe_candidate_id(self):
        with self.assertRaisesRegex(ValueError, "safe"):
            reserve(self.path, "../escape", "dua", "a"*64, "b"*64, "run")


if __name__ == "__main__":
    unittest.main()
