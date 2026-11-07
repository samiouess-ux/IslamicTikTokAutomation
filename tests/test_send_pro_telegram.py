"""Offline tests for the Dua & Adhkar Pro Telegram sender."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from send_pro_telegram import build_caption, send_video, MAX_CAPTION_CHARS, TelegramAcceptedLedgerError
from pro_delivery_ledger import load_ledger


class ProTelegramSenderTests(unittest.TestCase):
    def valid(self):
        return {
            "manifest_id": "dua-manifest-1",
            "content_type": "dua",
            "review_only": True,
            "auto_publish": False,
            "title_ar": "دعاء",
            "arabic_caption": "رَبَّنَا آتِنَا",
            "english_caption": "Our Lord, grant us good.",
        }

    def test_caption_is_branded_as_dua_adhkar_pro(self):
        caption = build_caption(self.valid())
        self.assertIn("DUA & ADHKAR PRO", caption)
        self.assertIn("للمراجعة فقط", caption)
        self.assertNotIn("QURAN PRO", caption)

    def test_rejects_quran_content(self):
        data = self.valid()
        data["content_type"] = "quran"
        with self.assertRaisesRegex(ValueError, "dua/dhikr only"):
            build_caption(data)

    def test_requires_manual_review_and_no_auto_publish(self):
        data = self.valid()
        data["review_only"] = False
        with self.assertRaisesRegex(ValueError, "review_only"):
            build_caption(data)
        data = self.valid()
        data["auto_publish"] = True
        with self.assertRaisesRegex(ValueError, "auto_publish"):
            build_caption(data)

    def test_rejects_caption_over_telegram_limit(self):
        data = self.valid()
        data["english_caption"] = "x" * MAX_CAPTION_CHARS
        with self.assertRaisesRegex(ValueError, "exceeds"):
            build_caption(data)

    def test_send_video_records_confirmed_delivery_in_ledger(self):
        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self):
                return json.dumps({"ok": True, "result": {"message_id": 321}}).encode()

        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            video = folder / "review.mp4"
            video.write_bytes(b"fake-mp4")
            caption = folder / "caption.json"
            caption.write_text(json.dumps(self.valid()), encoding="utf-8")
            ledger = folder / "ledger.json"
            with mock.patch("send_pro_telegram.urllib.request.urlopen", return_value=FakeResponse()):
                message = send_video(video, caption, "token", "chat", "run-1", ledger)
            self.assertEqual(message["message_id"], 321)
            entry = load_ledger(ledger)["entries"]["dua-manifest-1"]
            self.assertEqual(entry["state"], "delivered")
            self.assertEqual(entry["telegram_message_id"], 321)

    def test_confirmed_telegram_acceptance_with_receipt_failure_is_distinct(self):
        class FakeResponse:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def read(self):
                return json.dumps({"ok": True, "result": {"message_id": 987}}).encode()

        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            video = folder / "review.mp4"
            video.write_bytes(b"fake-mp4")
            caption = folder / "caption.json"
            caption.write_text(json.dumps(self.valid()), encoding="utf-8")
            ledger = folder / "ledger.json"
            with mock.patch("send_pro_telegram.urllib.request.urlopen", return_value=FakeResponse()):
                with mock.patch("send_pro_telegram.transition", side_effect=OSError("disk detail")):
                    with self.assertRaises(TelegramAcceptedLedgerError) as caught:
                        send_video(video, caption, "token", "chat", "run-1", ledger)
            self.assertIn("Telegram accepted", str(caught.exception))
            self.assertNotIn("disk detail", str(caught.exception))
            self.assertIsNone(caught.exception.__cause__)

    def test_pre_persisted_mode_refuses_wrong_run_before_telegram(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            video = folder / "review.mp4"
            video.write_bytes(b"fake-mp4")
            caption = folder / "caption.json"
            caption.write_text(json.dumps(self.valid()), encoding="utf-8")
            ledger = folder / "ledger.json"
            from pro_delivery_ledger import reserve
            reserve(ledger, "dua-manifest-1", "dua", "run-owner")
            with mock.patch("send_pro_telegram.urllib.request.urlopen") as send_mock:
                with self.assertRaisesRegex(ValueError, "different workflow run"):
                    send_video(video, caption, "token", "chat", "run-other", ledger,
                               reservation_persisted=True)
                send_mock.assert_not_called()

    def test_pre_persisted_mode_refuses_missing_reservation_before_telegram(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            video = folder / "review.mp4"
            video.write_bytes(b"fake-mp4")
            caption = folder / "caption.json"
            caption.write_text(json.dumps(self.valid()), encoding="utf-8")
            ledger = folder / "ledger.json"
            with mock.patch("send_pro_telegram.urllib.request.urlopen") as send_mock:
                with self.assertRaisesRegex(ValueError, "No persisted reservation"):
                    send_video(video, caption, "token", "chat", "run-1", ledger,
                               reservation_persisted=True)
                send_mock.assert_not_called()

    def test_pre_persisted_transport_failure_marks_reservation_uncertain(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            video = folder / "review.mp4"
            video.write_bytes(b"fake-mp4")
            caption = folder / "caption.json"
            caption.write_text(json.dumps(self.valid()), encoding="utf-8")
            ledger = folder / "ledger.json"
            from pro_delivery_ledger import reserve
            reserve(ledger, "dua-manifest-1", "dua", "run-1")
            secret_url = "https://api.telegram.org/botTEST_SECRET_TOKEN/sendVideo"
            with mock.patch("send_pro_telegram.urllib.request.urlopen",
                            side_effect=RuntimeError(f"transport failed for {secret_url}")):
                with self.assertRaisesRegex(RuntimeError, "outcome is uncertain") as caught:
                    send_video(video, caption, "TEST_SECRET_TOKEN", "chat", "run-1", ledger,
                               reservation_persisted=True)
                self.assertNotIn("TEST_SECRET_TOKEN", str(caught.exception))
                self.assertIsNone(caught.exception.__cause__)
            entry = load_ledger(ledger)["entries"]["dua-manifest-1"]
            self.assertEqual(entry["state"], "uncertain")

    def test_pre_persisted_mode_sends_only_after_matching_reservation(self):
        class FakeResponse:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def read(self):
                return json.dumps({"ok": True, "result": {"message_id": 654}}).encode()

        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            video = folder / "review.mp4"
            video.write_bytes(b"fake-mp4")
            caption = folder / "caption.json"
            caption.write_text(json.dumps(self.valid()), encoding="utf-8")
            ledger = folder / "ledger.json"
            from pro_delivery_ledger import reserve
            reserve(ledger, "dua-manifest-1", "dua", "run-1")
            with mock.patch("send_pro_telegram.urllib.request.urlopen", return_value=FakeResponse()):
                message = send_video(video, caption, "token", "chat", "run-1", ledger,
                                     reservation_persisted=True)
            self.assertEqual(message["message_id"], 654)
            entry = load_ledger(ledger)["entries"]["dua-manifest-1"]
            self.assertEqual(entry["state"], "delivered")

    def test_token_is_redacted_when_uncertain_ledger_transition_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            video = folder / "review.mp4"
            video.write_bytes(b"fake-mp4")
            caption = folder / "caption.json"
            caption.write_text(json.dumps(self.valid()), encoding="utf-8")
            ledger = folder / "ledger.json"
            secret = "BOT_TOKEN_MUST_NOT_LEAK"
            with mock.patch("send_pro_telegram.urllib.request.urlopen",
                            side_effect=RuntimeError(f"https://api.telegram.org/bot{secret}/sendVideo")):
                with mock.patch("send_pro_telegram.transition",
                                side_effect=OSError(f"ledger failed while handling {secret}")):
                    with self.assertRaisesRegex(RuntimeError, "ledger could not be advanced") as caught:
                        send_video(video, caption, secret, "chat", "run-1", ledger)
            self.assertNotIn(secret, str(caught.exception))
            self.assertIsNone(caught.exception.__cause__)

    def test_uncertain_send_blocks_a_second_attempt(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            video = folder / "review.mp4"
            video.write_bytes(b"fake-mp4")
            caption = folder / "caption.json"
            caption.write_text(json.dumps(self.valid()), encoding="utf-8")
            ledger = folder / "ledger.json"
            with mock.patch("send_pro_telegram.urllib.request.urlopen", side_effect=TimeoutError("timeout")):
                with self.assertRaisesRegex(RuntimeError, "outcome is uncertain") as caught:
                    send_video(video, caption, "token", "chat", "run-1", ledger)
                self.assertNotIn("timeout", str(caught.exception))
                self.assertIsNone(caught.exception.__cause__)
            self.assertEqual(load_ledger(ledger)["entries"]["dua-manifest-1"]["state"], "uncertain")
            with mock.patch("send_pro_telegram.urllib.request.urlopen") as send_mock:
                with self.assertRaisesRegex(ValueError, "refusing duplicate"):
                    send_video(video, caption, "token", "chat", "run-2", ledger)
                send_mock.assert_not_called()


    def test_build_caption_rejects_non_object_json_roots(self):
        for value in (None, [], "caption", 7):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "Caption JSON must contain an object"):
                    build_caption(value)

    def test_invalid_telegram_message_ids_are_marked_uncertain(self):
        class FakeResponse:
            def __init__(self, message_id):
                self.message_id = message_id
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def read(self):
                return json.dumps({"ok": True, "result": {"message_id": self.message_id}}).encode()

        for invalid_id in (True, 0, -1, "321", None):
            with self.subTest(message_id=invalid_id), tempfile.TemporaryDirectory() as tmp:
                folder = Path(tmp)
                video = folder / "review.mp4"
                video.write_bytes(b"fake-mp4")
                caption = folder / "caption.json"
                caption.write_text(json.dumps(self.valid()), encoding="utf-8")
                ledger = folder / "ledger.json"
                with mock.patch("send_pro_telegram.urllib.request.urlopen",
                                return_value=FakeResponse(invalid_id)):
                    with self.assertRaisesRegex(RuntimeError, "valid message_id"):
                        send_video(video, caption, "token", "chat", "run-1", ledger)
                self.assertEqual(
                    load_ledger(ledger)["entries"]["dua-manifest-1"]["state"],
                    "uncertain",
                )

    def test_truthy_non_boolean_telegram_ok_is_not_a_delivery_confirmation(self):
        class FakeResponse:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def read(self):
                return json.dumps({"ok": "true", "result": {"message_id": 321}}).encode()

        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            video = folder / "review.mp4"
            video.write_bytes(b"fake-mp4")
            caption = folder / "caption.json"
            caption.write_text(json.dumps(self.valid()), encoding="utf-8")
            ledger = folder / "ledger.json"
            with mock.patch("send_pro_telegram.urllib.request.urlopen", return_value=FakeResponse()):
                with self.assertRaisesRegex(RuntimeError, "did not confirm"):
                    send_video(video, caption, "token", "chat", "run-1", ledger)
            self.assertEqual(load_ledger(ledger)["entries"]["dua-manifest-1"]["state"], "uncertain")

    def test_non_object_telegram_response_is_marked_uncertain(self):
        class FakeResponse:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def read(self):
                return b"null"

        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            video = folder / "review.mp4"
            video.write_bytes(b"fake-mp4")
            caption = folder / "caption.json"
            caption.write_text(json.dumps(self.valid()), encoding="utf-8")
            ledger = folder / "ledger.json"
            with mock.patch("send_pro_telegram.urllib.request.urlopen", return_value=FakeResponse()):
                with self.assertRaisesRegex(RuntimeError, "did not confirm"):
                    send_video(video, caption, "token", "chat", "run-1", ledger)
            self.assertEqual(load_ledger(ledger)["entries"]["dua-manifest-1"]["state"], "uncertain")



if __name__ == "__main__":
    unittest.main()
