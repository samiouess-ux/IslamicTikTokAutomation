"""Offline safety tests for the isolated Pro candidate-preview Telegram sender."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import send_pro_preview_telegram as sender


class ProPreviewTelegramSenderTests(unittest.TestCase):
    def manifest(self):
        return {
            "id": "preview-dua-001",
            "content_type": "dua",
            "lifecycle_status": "candidate_preview",
            "preview_only": True,
            "rotation_approved": False,
            "title_ar": "دعاء تجريبي",
            "items": [{
                "id": "item-1", "kind": "quranic_dua",
                "arabic": "رَبَّنَا آتِنَا فِي الدُّنْيَا حَسَنَةً",
                "source_name": "Quran", "source_url": "https://example.org/quran",
                "source_reference": "Al-Baqarah 2:201",
                "verification_status": "verified", "human_reviewed": False,
            }],
            "audio": {"kind": "silent", "music_allowed": False},
            "visual": {"template": "ornate_gold_classic", "background_candidate": {
                "source_url": "https://example.org/source",
                "direct_video_url": "https://example.org/background.mp4",
                "approved": True, "user_approved": True,
            }},
            "publishing": {"approval_required": True, "auto_publish": False},
        }

    def files(self, folder):
        manifest = folder / "candidate.json"
        manifest.write_text(json.dumps(self.manifest(), ensure_ascii=False), encoding="utf-8")
        video = folder / "PREVIEW-ONLY-dua-preview-dua-001.mp4"
        video.write_bytes(b"fake-mp4")
        return video, manifest

    def test_explicit_confirmation_is_required_before_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            video, manifest = self.files(Path(tmp))
            with patch.object(sender.urllib.request, "urlopen") as call:
                with self.assertRaisesRegex(PermissionError, "Explicit"):
                    sender.send_preview(video, manifest, "token", "12345")
                call.assert_not_called()

    def test_production_or_rotation_approved_manifest_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            video, manifest = self.files(Path(tmp))
            data = self.manifest()
            data["lifecycle_status"] = "production_approved"
            manifest.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Only candidate_preview"):
                sender.send_preview(video, manifest, "token", "12345", confirmed=True)
            data["lifecycle_status"] = "candidate_preview"
            data["rotation_approved"] = True
            manifest.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "must not be approved"):
                sender.send_preview(video, manifest, "token", "12345", confirmed=True)

    def test_only_preview_filename_and_private_numeric_chat_are_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            video, manifest = self.files(Path(tmp))
            video.rename(Path(tmp) / "dua.mp4")
            with self.assertRaisesRegex(ValueError, "PREVIEW-ONLY"):
                sender.send_preview(Path(tmp) / "dua.mp4", manifest, "token", "12345", confirmed=True)
            video = Path(tmp) / "PREVIEW-ONLY-dua-preview-dua-001.mp4"
            video.write_bytes(b"fake-mp4")
            with self.assertRaisesRegex(ValueError, "positive numeric private-chat"):
                sender.send_preview(video, manifest, "token", "-100123", confirmed=True)

    def test_video_filename_must_match_exact_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            video, manifest = self.files(Path(tmp))
            wrong = Path(tmp) / "PREVIEW-ONLY-dua-another-id.mp4"
            video.rename(wrong)
            with self.assertRaisesRegex(ValueError, "exactly match"):
                sender.send_preview(wrong, manifest, "token", "12345", confirmed=True)

    def test_caption_clearly_marks_not_approved_for_posting(self):
        caption = sender.build_preview_caption(self.manifest())
        self.assertTrue(caption.startswith("PREVIEW — NOT APPROVED FOR POSTING"))
        self.assertIn("لا تنشر هذا الفيديو", caption)

    def test_confirmed_preview_sends_once_and_does_not_touch_production_state(self):
        class Response:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def read(self):
                return b'{"ok":true,"result":{"message_id":77}}'

        with tempfile.TemporaryDirectory() as tmp:
            video, manifest = self.files(Path(tmp))
            with patch.object(sender.urllib.request, "urlopen", return_value=Response()) as call:
                result = sender.send_preview(video, manifest, "token", "12345", confirmed=True)
            self.assertEqual(call.call_count, 1)
            self.assertEqual(result["message_id"], 77)
            self.assertTrue(result["preview_only"])
            self.assertFalse(result["production_ledger_touched"])
            self.assertFalse(result["rotation_history_touched"])
            self.assertFalse(result["tiktok_published"])

    def test_transport_error_is_not_retried(self):
        with tempfile.TemporaryDirectory() as tmp:
            video, manifest = self.files(Path(tmp))
            with patch.object(sender.urllib.request, "urlopen", side_effect=TimeoutError("unknown")) as call:
                with self.assertRaises(TimeoutError):
                    sender.send_preview(video, manifest, "token", "12345", confirmed=True)
            self.assertEqual(call.call_count, 1)


if __name__ == "__main__":
    unittest.main()
