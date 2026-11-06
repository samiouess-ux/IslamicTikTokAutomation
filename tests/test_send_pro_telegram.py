"""Offline tests for the Dua & Adhkar Pro Telegram sender."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from send_pro_telegram import build_caption, MAX_CAPTION_CHARS


class ProTelegramSenderTests(unittest.TestCase):
    def valid(self):
        return {
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


if __name__ == "__main__":
    unittest.main()
