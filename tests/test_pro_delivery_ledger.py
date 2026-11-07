"""Offline tests for Pro delivery reservation state transitions."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from pro_delivery_ledger import reserve, transition, reconcile_not_delivered, assert_reserved_for_run


class ProDeliveryLedgerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ledger = Path(self.tmp.name) / "ledger.json"

    def tearDown(self):
        self.tmp.cleanup()

    def test_reservation_blocks_duplicate(self):
        reserve(self.ledger, "dua-1", "dua", "run-1")
        with self.assertRaisesRegex(ValueError, "refusing duplicate"):
            reserve(self.ledger, "dua-1", "dua", "run-2")

    def test_pre_persisted_reservation_is_bound_to_run_and_type(self):
        reserve(self.ledger, "dua-pre", "dua", "run-expected")
        entry = assert_reserved_for_run(self.ledger, "dua-pre", "dua", "run-expected")
        self.assertEqual(entry["state"], "reserved")
        with self.assertRaisesRegex(ValueError, "different workflow run"):
            assert_reserved_for_run(self.ledger, "dua-pre", "dua", "run-other")
        with self.assertRaisesRegex(ValueError, "content type"):
            assert_reserved_for_run(self.ledger, "dua-pre", "dhikr", "run-expected")
        with self.assertRaisesRegex(ValueError, "No persisted reservation"):
            assert_reserved_for_run(self.ledger, "missing", "dua", "run-expected")

    def test_persisted_reservation_rejects_non_string_content_type(self):
        reserve(self.ledger, "dua-type", "dua", "run-1")
        for content_type in ([], {}, 7, True):
            with self.subTest(content_type=content_type), self.assertRaisesRegex(ValueError, "Only dua/dhikr"):
                assert_reserved_for_run(self.ledger, "dua-type", content_type, "run-1")

    def test_confirmed_delivery_requires_message_id(self):
        reserve(self.ledger, "dhikr-1", "dhikr", "run-1")
        with self.assertRaisesRegex(ValueError, "message_id"):
            transition(self.ledger, "dhikr-1", "delivered")
        entry = transition(self.ledger, "dhikr-1", "delivered", 123)
        self.assertEqual(entry["state"], "delivered")
        self.assertEqual(entry["telegram_message_id"], 123)

    def test_uncertain_entry_blocks_resend_until_human_reconciliation(self):
        reserve(self.ledger, "dua-2", "dua", "run-1")
        transition(self.ledger, "dua-2", "uncertain")
        with self.assertRaisesRegex(ValueError, "refusing duplicate"):
            reserve(self.ledger, "dua-2", "dua", "run-2")
        with self.assertRaisesRegex(ValueError, "Explicit"):
            reconcile_not_delivered(self.ledger, "dua-2", "yes")
        reconcile_not_delivered(self.ledger, "dua-2", "CONFIRM_NOT_DELIVERED")
        reserve(self.ledger, "dua-2", "dua", "run-3")

    def test_load_rejects_boolean_version_and_non_string_state(self):
        for payload in (
            {"version": True, "entries": {}},
            {"version": 1, "entries": {"dua-x": {"state": []}}},
            {"version": 1, "entries": {"dua-x": {"state": {}}}},
        ):
            with self.subTest(payload=payload):
                self.ledger.write_text(__import__("json").dumps(payload), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "Invalid Pro reservation ledger"):
                    from pro_delivery_ledger import load_ledger
                    load_ledger(self.ledger)

    def test_delivered_entry_is_terminal(self):
        reserve(self.ledger, "dua-3", "dua", "run-1")
        transition(self.ledger, "dua-3", "delivered", 456)
        with self.assertRaisesRegex(ValueError, "Invalid ledger transition"):
            transition(self.ledger, "dua-3", "uncertain")

    def test_rejects_invalid_content_type_and_boolean_message_id(self):
        with self.assertRaisesRegex(ValueError, "Only dua/dhikr"):
            reserve(self.ledger, "bad", "quran", "run-1")
        reserve(self.ledger, "dua-4", "dua", "run-1")
        with self.assertRaisesRegex(ValueError, "positive Telegram"):
            transition(self.ledger, "dua-4", "delivered", True)


if __name__ == "__main__":
    unittest.main()
