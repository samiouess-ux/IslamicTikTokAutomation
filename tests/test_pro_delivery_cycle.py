"""Offline tests for the fail-closed Pro two-phase delivery cycle."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pro_delivery_cycle import run_delivery_cycle
from pro_delivery_ledger import load_ledger, transition


class ProDeliveryCycleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.ledger = self.root / "data" / "pro_delivery_ledger.json"
        self.caption = self.root / "caption.json"
        self.caption.write_text(json.dumps({
            "manifest_id": "dua-cycle-1",
            "content_type": "dua",
            "review_only": True,
            "auto_publish": False,
        }), encoding="utf-8")
        self.video = self.root / "review.mp4"
        self.video.write_bytes(b"fake-video")

    def tearDown(self):
        self.tmp.cleanup()

    def run_cycle(self, **overrides):
        args = {
            "repo_path": self.root,
            "ledger_path": self.ledger,
            "video_path": self.video,
            "caption_path": self.caption,
            "token": "test-token",
            "chat_id": "test-chat",
            "run_id": "run-123",
        }
        args.update(overrides)
        return run_delivery_cycle(**args)

    def test_first_persistence_failure_prevents_sender(self):
        with mock.patch("pro_delivery_cycle.persist_ledger",
                        side_effect=RuntimeError("push rejected")) as persist_mock:
            with mock.patch("pro_delivery_cycle.send_video") as send_mock:
                with self.assertRaisesRegex(RuntimeError, "push rejected"):
                    self.run_cycle(persist_fn=persist_mock, send_fn=send_mock)
        send_mock.assert_not_called()
        self.assertEqual(load_ledger(self.ledger)["entries"]["dua-cycle-1"]["state"], "reserved")

    def test_noop_first_persistence_result_prevents_sender(self):
        with mock.patch("pro_delivery_cycle.send_video") as send_mock:
            with self.assertRaisesRegex(RuntimeError, "refusing Telegram"):
                self.run_cycle(persist_fn=lambda repo: False, send_fn=send_mock)
        send_mock.assert_not_called()

    def test_rejects_ledger_outside_branch_persisted_path(self):
        other_ledger = self.root / "elsewhere.json"
        with self.assertRaisesRegex(ValueError, "Ledger path must match"):
            self.run_cycle(ledger_path=other_ledger)

    def test_ambiguous_sender_failure_persists_uncertain_state(self):
        def fake_send(*args, **kwargs):
            transition(self.ledger, "dua-cycle-1", "uncertain")
            raise TimeoutError("ambiguous timeout")

        persist_mock = mock.Mock(return_value=True)
        with self.assertRaisesRegex(TimeoutError, "ambiguous timeout"):
            self.run_cycle(persist_fn=persist_mock, send_fn=fake_send)
        self.assertEqual(persist_mock.call_count, 2)
        self.assertEqual(load_ledger(self.ledger)["entries"]["dua-cycle-1"]["state"], "uncertain")

    def test_uncertain_outcome_persistence_failure_keeps_cycle_blocked(self):
        persist_mock = mock.Mock(side_effect=[True, RuntimeError("uncertain push failed")])

        def fake_send(*args, **kwargs):
            transition(self.ledger, "dua-cycle-1", "uncertain")
            raise TimeoutError("ambiguous Telegram timeout")

        with self.assertRaisesRegex(RuntimeError, "outcome-ledger persistence failed"):
            self.run_cycle(persist_fn=persist_mock, send_fn=fake_send)
        self.assertEqual(persist_mock.call_count, 2)
        self.assertEqual(load_ledger(self.ledger)["entries"]["dua-cycle-1"]["state"], "uncertain")

    def test_success_persists_before_and_after_sender(self):
        events = []

        def fake_persist(repo):
            events.append("persist")
            return True

        def fake_send(*args, **kwargs):
            events.append("send")
            self.assertIs(kwargs.get("reservation_persisted"), True)
            transition(self.ledger, "dua-cycle-1", "delivered", 777)
            return {"message_id": 777}

        result = self.run_cycle(persist_fn=fake_persist, send_fn=fake_send)
        self.assertEqual(result["message_id"], 777)
        self.assertEqual(events, ["persist", "send", "persist"])
        self.assertEqual(load_ledger(self.ledger)["entries"]["dua-cycle-1"]["state"], "delivered")

    def test_final_persistence_failure_leaves_reserved_commit_as_blocking_boundary(self):
        persist_mock = mock.Mock(side_effect=[True, RuntimeError("final push failed")])

        def fake_send(*args, **kwargs):
            transition(self.ledger, "dua-cycle-1", "delivered", 888)
            return {"message_id": 888}

        with self.assertRaisesRegex(RuntimeError, "final push failed"):
            self.run_cycle(persist_fn=persist_mock, send_fn=fake_send)
        self.assertEqual(persist_mock.call_count, 2)
        # The remote branch would still contain the first, already-pushed reservation.
        # The local file reflects the confirmed Telegram response but is not pushed.
        self.assertEqual(load_ledger(self.ledger)["entries"]["dua-cycle-1"]["state"], "delivered")


if __name__ == "__main__":
    unittest.main()
