"""Offline tests for Pro delivery reservation state transitions."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from pro_delivery_ledger import reserve, transition, reconcile_not_delivered


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
        with self.assertRaisesRegex(ValueError, "explicit"):
            reconcile_not_delivered(self.ledger, "dua-2", "yes")
        reconcile_not_delivered(self.ledger, "dua-2", "CONFIRM_NOT_DELIVERED")
        reserve(self.ledger, "dua-2", "dua", "run-3")

    def test_delivered_entry_is_terminal(self):
        reserve(self.ledger, "dua-3", "dua", "run-1")
        transition(self.ledger, "dua-3", "delivered", 456)
        with self.assertRaisesRegex(ValueError, "Invalid ledger transition"):
            transition(self.ledger, "dua-3", "uncertain")


if __name__ == "__main__":
    unittest.main()
