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
from send_pro_telegram import TelegramAcceptedLedgerError
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

    def test_rejects_symlinked_ledger_file_and_data_directory_before_reservation(self):
        outside = self.root / "outside-ledger.json"
        outside.write_text('{"outside": true}', encoding="utf-8")
        data_dir = self.root / "data"
        data_dir.mkdir()
        ledger_link = data_dir / "pro_delivery_ledger.json"
        try:
            ledger_link.symlink_to(outside)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks are unavailable on this platform.")

        persist_mock = mock.Mock(return_value=True)
        send_mock = mock.Mock()
        with self.assertRaisesRegex(ValueError, "must not use symlinks"):
            self.run_cycle(persist_fn=persist_mock, send_fn=send_mock)
        persist_mock.assert_not_called()
        send_mock.assert_not_called()
        self.assertEqual(outside.read_text(encoding="utf-8"), '{"outside": true}')

        ledger_link.unlink()
        data_dir.rmdir()
        outside_dir = self.root / "outside-data"
        outside_dir.mkdir()
        (outside_dir / "pro_delivery_ledger.json").write_text("{}", encoding="utf-8")
        data_dir.symlink_to(outside_dir, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "must not use symlinks"):
            self.run_cycle(persist_fn=persist_mock, send_fn=send_mock)
        persist_mock.assert_not_called()
        send_mock.assert_not_called()

    def test_confirmed_telegram_acceptance_is_not_reclassified_as_uncertain(self):
        persist_mock = mock.Mock(return_value=True)
        def accepted_but_receipt_failed(*args, **kwargs):
            raise TelegramAcceptedLedgerError("safe sender-level accepted-send signal")

        with self.assertRaisesRegex(RuntimeError, "Telegram accepted the Pro review video") as caught:
            self.run_cycle(persist_fn=persist_mock, send_fn=accepted_but_receipt_failed)
        self.assertIn("do not resend", str(caught.exception))
        self.assertNotIn("uncertain", str(caught.exception).lower())
        self.assertIsNone(caught.exception.__cause__)
        # Only the initial reservation is pushed; no false uncertain transition is attempted.
        self.assertEqual(persist_mock.call_count, 1)
        self.assertEqual(load_ledger(self.ledger)["entries"]["dua-cycle-1"]["state"], "reserved")

    def test_ambiguous_sender_failure_persists_uncertain_state(self):
        def fake_send(*args, **kwargs):
            transition(self.ledger, "dua-cycle-1", "uncertain")
            raise TimeoutError("ambiguous timeout")

        persist_mock = mock.Mock(return_value=True)
        with self.assertRaisesRegex(RuntimeError, "outcome is not confirmed") as caught:
            self.run_cycle(persist_fn=persist_mock, send_fn=fake_send)
        self.assertNotIn("ambiguous timeout", str(caught.exception))
        self.assertIsNone(caught.exception.__cause__)
        self.assertEqual(persist_mock.call_count, 2)
        self.assertEqual(load_ledger(self.ledger)["entries"]["dua-cycle-1"]["state"], "uncertain")

    def test_uncertain_outcome_persistence_failure_keeps_cycle_blocked(self):
        secret = "GITHUB_REMOTE_TOKEN_SECRET"
        persist_mock = mock.Mock(side_effect=[True, RuntimeError(f"push failed for https://{secret}@github.com/owner/repo")])

        def fake_send(*args, **kwargs):
            transition(self.ledger, "dua-cycle-1", "uncertain")
            raise TimeoutError("ambiguous Telegram timeout")

        with self.assertRaisesRegex(RuntimeError, "outcome-ledger persistence failed") as caught:
            self.run_cycle(persist_fn=persist_mock, send_fn=fake_send)
        self.assertNotIn(secret, str(caught.exception))
        self.assertIsNone(caught.exception.__cause__)
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

    def test_final_persistence_failure_after_confirmed_send_is_safe_and_blocks_resend(self):
        secret = "GITHUB_REMOTE_TOKEN_SECRET"
        persist_mock = mock.Mock(side_effect=[
            True, RuntimeError(f"final push failed for https://{secret}@github.com/owner/repo")
        ])

        def fake_send(*args, **kwargs):
            transition(self.ledger, "dua-cycle-1", "delivered", 888)
            return {"message_id": 888}

        with self.assertRaisesRegex(RuntimeError, "Telegram accepted the Pro review video") as caught:
            self.run_cycle(persist_fn=persist_mock, send_fn=fake_send)
        self.assertNotIn(secret, str(caught.exception))
        self.assertIsNone(caught.exception.__cause__)
        self.assertIn("do not resend", str(caught.exception))
        self.assertEqual(persist_mock.call_count, 2)
        # The remote branch still has the first, already-pushed reservation.
        # The local file has the confirmed receipt but final push failed.
        entry = load_ledger(self.ledger)["entries"]["dua-cycle-1"]
        self.assertEqual(entry["state"], "delivered")
        self.assertEqual(entry["telegram_message_id"], 888)


    def test_non_object_caption_json_is_rejected_before_reservation(self):
        for raw in ("null", "[]", '"caption"'):
            with self.subTest(raw=raw):
                self.caption.write_text(raw, encoding="utf-8")
                with mock.patch("pro_delivery_cycle.send_video") as send_mock:
                    with self.assertRaisesRegex(ValueError, "Caption JSON must contain an object"):
                        self.run_cycle(send_fn=send_mock)
                send_mock.assert_not_called()
                self.assertFalse(self.ledger.exists())



if __name__ == "__main__":
    unittest.main()
