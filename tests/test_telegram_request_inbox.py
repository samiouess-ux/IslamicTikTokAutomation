import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from telegram_request_inbox import extract_authorized_request


class TelegramRequestInboxTests(unittest.TestCase):
    def setUp(self):
        self.update = {
            "update_id": 987,
            "message": {
                "message_id": 12,
                "text": "فيديو سورة الرحمن",
                "chat": {"id": 123456, "type": "private"},
                "from": {"id": 123456},
            },
        }

    def test_authorized_message_is_parsed_without_side_effects(self):
        result = extract_authorized_request(self.update, "123456")
        self.assertEqual(result["update_id"], 987)
        self.assertEqual(result["request"]["surah_name"], "الرحمن")
        self.assertEqual(result["status"], "authorized_request_parsed_only")
        self.assertFalse(result["rendering_allowed"])
        self.assertFalse(result["telegram_delivery"])
        self.assertFalse(result["auto_publish"])

    def test_unauthorized_chat_is_rejected_before_parsing(self):
        with self.assertRaises(PermissionError):
            extract_authorized_request(self.update, "999")

    def test_non_text_message_is_rejected(self):
        self.update["message"].pop("text")
        with self.assertRaisesRegex(ValueError, "text request"):
            extract_authorized_request(self.update, "123456")


if __name__ == "__main__":
    unittest.main()
