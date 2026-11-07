"""Offline safety tests for the isolated Pro candidate-preview Telegram sender."""
import json
import hashlib
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
            "source": {
                "name": "Quran.com",
                "url": "https://quran.com/2/201",
                "reference": "Al-Baqarah 2:201",
            },
            "title_ar": "دعاء تجريبي",
            "items": [{
                "id": "item-1", "kind": "quranic_dua",
                "arabic": "رَبَّنَا آتِنَا فِي الدُّنْيَا حَسَنَةً",
                "source_name": "Quran", "source_url": "https://example.org/quran",
                "source_reference": "Al-Baqarah 2:201",
                "verification_status": "verified", "human_reviewed": False,
            }],
            "audio": {"kind": "silent", "music_allowed": False},
            "media_assets": [{"asset_id": "bg-001", "media_type": "visual"}],
            "visual": {"template": "ornate_gold_classic", "background_candidate": {"asset_id": "bg-001",
                "source_url": "https://example.org/source",
                "direct_video_url": "https://example.org/background.mp4",
                "approved": True, "user_approved": True,
            }},
            "publishing": {"approval_required": True, "auto_publish": False},
            "review_delivery_territory": "Tunisia",
        }

    def files(self, folder):
        (folder / "content/pro").mkdir(parents=True)
        (folder / "output/pro_preview").mkdir(parents=True)
        manifest = folder / "content/pro/candidate.json"
        manifest.write_text(json.dumps(self.manifest(), ensure_ascii=False), encoding="utf-8")
        video = folder / "output/pro_preview/PREVIEW-ONLY-dua-preview-dua-001.mp4"
        video.write_bytes(b"fake-mp4")
        (folder / "assets/pro/media").mkdir(parents=True)
        (folder / "content/pro/rights").mkdir(parents=True)
        media = folder / "assets/pro/media/bg.mp4"
        media.write_bytes(b"approved-background")
        record = {
            "schema_version": 1, "asset_id": "bg-001", "media_type": "visual",
            "file_path": "assets/pro/media/bg.mp4",
            "file_sha256": hashlib.sha256(media.read_bytes()).hexdigest(),
            "source_page_url": "https://example.org/source", "creator_or_performer": "Creator",
            "rights_owner": "Rights owner", "source_platform": "Example stock",
            "downloaded_at": "2026-01-01T00:00:00Z", "license_name": "Example license",
            "license_evidence": {"kind": "url", "value": "https://example.org/license"},
            "intended_uses": {"download": True, "editing": True, "video_synchronization": True,
                "private_review_delivery": True, "public_social_posting": True,
                "commercial_monetized_use": True},
            "territories": ["worldwide"], "validity": {"start": "2025-01-01", "end": None},
            "attribution": {"required": False},
            "third_party_review": {key: {"reviewed": True, "resolved": True, "notes": "Reviewed; no unresolved third-party rights identified."}
                for key in ("people", "logos_trademarks", "artwork", "property_privacy", "endorsement")},
            "reviewer": "Human reviewer", "reviewed_at": "2026-01-02T00:00:00Z",
            "decision": "approved",
        }
        (folder / "content/pro/rights/bg-001.json").write_text(json.dumps(record), encoding="utf-8")
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
                sender.send_preview(video, manifest, "token", "12345", confirmed=True, repo_root=Path(tmp))
            data["lifecycle_status"] = "candidate_preview"
            data["rotation_approved"] = True
            manifest.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "must not be approved"):
                sender.send_preview(video, manifest, "token", "12345", confirmed=True, repo_root=Path(tmp))

    def test_only_preview_filename_and_private_numeric_chat_are_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            video, manifest = self.files(Path(tmp))
            video.rename(Path(tmp) / "output/pro_preview/dua.mp4")
            with self.assertRaisesRegex(ValueError, "PREVIEW-ONLY"):
                sender.send_preview(Path(tmp) / "output/pro_preview/dua.mp4", manifest, "token", "12345", confirmed=True, repo_root=Path(tmp))
            video = Path(tmp) / "output/pro_preview/PREVIEW-ONLY-dua-preview-dua-001.mp4"
            video.write_bytes(b"fake-mp4")
            with self.assertRaisesRegex(ValueError, "positive numeric private-chat"):
                sender.send_preview(video, manifest, "token", "-100123", confirmed=True, repo_root=Path(tmp))

    def test_video_filename_must_match_exact_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            video, manifest = self.files(Path(tmp))
            wrong = Path(tmp) / "output/pro_preview/PREVIEW-ONLY-dua-another-id.mp4"
            video.rename(wrong)
            with self.assertRaisesRegex(ValueError, "exactly match"):
                sender.send_preview(wrong, manifest, "token", "12345", confirmed=True, repo_root=Path(tmp))

    def test_caption_clearly_marks_not_approved_for_posting(self):
        caption = sender.build_preview_caption(self.manifest())
        self.assertTrue(caption.startswith("PREVIEW — NOT APPROVED FOR POSTING"))
        self.assertIn("لا تنشر هذا الفيديو", caption)

    def test_confirmed_preview_sends_once_and_does_not_touch_production_state(self):
        class Response:
            def __init__(self, payload):
                self.payload = payload
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def read(self):
                return json.dumps(self.payload).encode()

        with tempfile.TemporaryDirectory() as tmp:
            video, manifest = self.files(Path(tmp))
            chat = Response({"ok": True, "result": {"id": 12345, "type": "private"}})
            sent = Response({"ok": True, "result": {"message_id": 77}})
            with patch.object(sender.urllib.request, "urlopen", side_effect=[chat, sent]) as call:
                result = sender.send_preview(video, manifest, "token", "12345",
                    confirmed=True, repo_root=Path(tmp))
            self.assertEqual(call.call_count, 2)
            self.assertEqual(result["message_id"], 77)
            self.assertTrue(result["preview_only"])
            self.assertFalse(result["production_ledger_touched"])
            self.assertFalse(result["rotation_history_touched"])
            self.assertFalse(result["tiktok_published"])


    def test_uploaded_bytes_must_match_reserved_hashes_before_network(self):
        import hashlib
        with tempfile.TemporaryDirectory() as tmp:
            video, manifest = self.files(Path(tmp))
            expected_video = hashlib.sha256(video.read_bytes()).hexdigest()
            expected_manifest = hashlib.sha256(manifest.read_bytes()).hexdigest()
            with patch.object(sender.urllib.request, "urlopen") as call:
                with self.assertRaisesRegex(ValueError, "video bytes do not match"):
                    sender.send_preview(video, manifest, "token", "12345", confirmed=True,
                        expected_video_sha256="0" * 64,
                        expected_manifest_sha256=expected_manifest, repo_root=Path(tmp))
                call.assert_not_called()
            with patch.object(sender.urllib.request, "urlopen") as call:
                with self.assertRaisesRegex(ValueError, "manifest bytes do not match"):
                    sender.send_preview(video, manifest, "token", "12345", confirmed=True,
                        expected_video_sha256=expected_video,
                        expected_manifest_sha256="0" * 64, repo_root=Path(tmp))
                call.assert_not_called()

    def test_transport_error_is_not_retried(self):
        with tempfile.TemporaryDirectory() as tmp:
            video, manifest = self.files(Path(tmp))
            chat = type("Response", (), {"__enter__": lambda self: self,
                "__exit__": lambda self, *args: False,
                "read": lambda self: b'{"ok":true,"result":{"id":12345,"type":"private"}}'})()
            with patch.object(sender.urllib.request, "urlopen", side_effect=[chat, TimeoutError("unknown")]) as call:
                with self.assertRaisesRegex(RuntimeError, "outcome is uncertain"):
                    sender.send_preview(video, manifest, "token", "12345", confirmed=True, repo_root=Path(tmp))
            self.assertEqual(call.call_count, 2)


    def test_non_private_chat_blocks_upload(self):
        class Response:
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def read(self): return b'{"ok":true,"result":{"id":12345,"type":"group"}}'
        with tempfile.TemporaryDirectory() as tmp:
            video, manifest = self.files(Path(tmp))
            with patch.object(sender.urllib.request, "urlopen", return_value=Response()) as call:
                with self.assertRaisesRegex(RuntimeError, "not a private chat"):
                    sender.send_preview(video, manifest, "token", "12345", confirmed=True, repo_root=Path(tmp))
            self.assertEqual(call.call_count, 1)

    def test_mismatched_chat_id_blocks_upload(self):
        class Response:
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def read(self): return b'{"ok":true,"result":{"id":99999,"type":"private"}}'
        with tempfile.TemporaryDirectory() as tmp:
            video, manifest = self.files(Path(tmp))
            with patch.object(sender.urllib.request, "urlopen", return_value=Response()) as call:
                with self.assertRaisesRegex(RuntimeError, "different destination"):
                    sender.send_preview(video, manifest, "token", "12345", confirmed=True, repo_root=Path(tmp))
            self.assertEqual(call.call_count, 1)

    def test_malformed_or_failed_getchat_blocks_upload_without_leaking_token(self):
        class Response:
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def read(self): return b'{"ok":true,"result":null}'
        with tempfile.TemporaryDirectory() as tmp:
            video, manifest = self.files(Path(tmp))
            with patch.object(sender.urllib.request, "urlopen", return_value=Response()) as call:
                with self.assertRaisesRegex(RuntimeError, "malformed data"):
                    sender.send_preview(video, manifest, "secret-token", "12345", confirmed=True, repo_root=Path(tmp))
            self.assertEqual(call.call_count, 1)
            # The exception is deliberately generic; no token-bearing URL is exposed to callers.


    def test_supergroup_and_channel_destinations_are_rejected(self):
        for chat_type in ("supergroup", "channel"):
            class Response:
                def __enter__(self): return self
                def __exit__(self, *args): return False
                def read(self): return json.dumps({"ok": True, "result": {"id": 12345, "type": chat_type}}).encode()
            with self.subTest(chat_type=chat_type), tempfile.TemporaryDirectory() as tmp:
                video, manifest = self.files(Path(tmp))
                with patch.object(sender.urllib.request, "urlopen", return_value=Response()) as call:
                    with self.assertRaisesRegex(RuntimeError, "not a private chat"):
                        sender.send_preview(video, manifest, "token", "12345", confirmed=True, repo_root=Path(tmp))
                self.assertEqual(call.call_count, 1)

    def test_getchat_api_failure_is_redacted_and_blocks_upload(self):
        with tempfile.TemporaryDirectory() as tmp:
            video, manifest = self.files(Path(tmp))
            with patch.object(sender.urllib.request, "urlopen", side_effect=OSError("token-bearing fake URL")) as call:
                with self.assertRaisesRegex(RuntimeError, "verification failed") as caught:
                    sender.send_preview(video, manifest, "secret-token", "12345", confirmed=True, repo_root=Path(tmp))
            self.assertEqual(call.call_count, 1)
            self.assertNotIn("secret-token", str(caught.exception))
            self.assertNotIn("token-bearing fake URL", str(caught.exception))

if __name__ == "__main__":
    unittest.main()
