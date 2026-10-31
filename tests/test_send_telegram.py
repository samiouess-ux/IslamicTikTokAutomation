"""Unit tests for Telegram review delivery safeguards."""
import json, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src"))
from send_telegram import MAX_VIDEO_BYTES, build_caption, send_video
class TelegramDeliveryTests(unittest.TestCase):
    def test_caption_is_bilingual_and_review_only(self):
        caption = build_caption({"arabic_caption":"سورة الإخلاص","english_caption":"Surah Al-Ikhlas","hashtags_ar":["#القرآن"],"hashtags_en":["#Quran"]})
        self.assertIn("سورة الإخلاص", caption); self.assertIn("Surah Al-Ikhlas", caption); self.assertIn("لم يتم النشر على TikTok", caption)
    def test_caption_over_limit_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "1024"): build_caption({"english_caption":"x" * 1100})
    def test_missing_credentials_fail_before_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp); video=p/"review.mp4"; caption=p/"caption.json"; video.write_bytes(b"mp4"); caption.write_text("{}",encoding="utf-8")
            with patch("send_telegram.urllib.request.urlopen") as call:
                with self.assertRaisesRegex(ValueError,"GitHub Secrets"): send_video(video,caption,"","chat")
                call.assert_not_called()
    def test_successful_api_response_confirms_delivery(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp); video=p/"review.mp4"; caption=p/"caption.json"
            video.write_bytes(b"FAKE-MP4-BYTES")
            caption.write_text(json.dumps({"arabic_caption":"مراجعة","english_caption":"Review"}),encoding="utf-8")
            class Response:
                def __enter__(self): return self
                def __exit__(self,*args): return False
                def read(self): return b'{"ok":true,"result":{"message_id":123}}'
            with patch("send_telegram.urllib.request.urlopen", return_value=Response()) as call:
                message=send_video(video,caption,"token","chat-id")
            self.assertEqual(message["message_id"],123)
            request=call.call_args.args[0]
            self.assertIn("sendVideo",request.full_url)
            self.assertIn(b"FAKE-MP4-BYTES",request.data)
            self.assertIn("لم يتم النشر على TikTok".encode(),request.data)
    def test_over_50mb_fails_before_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp); video=p/"review.mp4"; caption=p/"caption.json"
            with video.open("wb") as f: f.truncate(MAX_VIDEO_BYTES+1)
            caption.write_text(json.dumps({}),encoding="utf-8")
            with patch("send_telegram.urllib.request.urlopen") as call:
                with self.assertRaisesRegex(ValueError,"50 MB"): send_video(video,caption,"token","chat")
                call.assert_not_called()
if __name__ == "__main__": unittest.main()
