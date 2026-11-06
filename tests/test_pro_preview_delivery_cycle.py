"""Offline orchestration tests; all persistence and Telegram calls are injected."""
import json
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from pro_preview_delivery_cycle import run_preview_cycle


def manifest_data():
    return {
        "id":"candidate-001", "content_type":"dua", "lifecycle_status":"candidate_preview",
        "preview_only":True, "rotation_approved":False, "title_ar":"دعاء",
        "source":{"name":"Quran.com","url":"https://quran.com/2/201","reference":"2:201"},
        "items":[{"id":"item-1","kind":"quranic_dua","arabic":"رَبَّنَا آتِنَا",
            "source_name":"Quran","source_url":"https://quran.com/2/201","source_reference":"2:201",
            "verification_status":"verified","human_reviewed":False}],
        "audio":{"kind":"silent","music_allowed":False},
        "media_assets":[{"asset_id":"bg-001","media_type":"visual"}],
        "visual":{"template":"ornate_gold_classic","background_candidate":{"asset_id":"bg-001",
            "source_url":"https://example.org/source","direct_video_url":"https://example.org/bg.mp4",
            "approved":True,"user_approved":True}},
        "publishing":{"approval_required":True,"auto_publish":False}
    }


class PreviewCycleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "content/pro").mkdir(parents=True)
        (self.root / "output/pro_preview").mkdir(parents=True)
        (self.root / "data").mkdir()
        self.manifest = self.root / "content/pro/candidate.json"
        self.manifest.write_text(json.dumps(manifest_data(), ensure_ascii=False), encoding="utf-8")
        self.video = self.root / "output/pro_preview/PREVIEW-ONLY-dua-candidate-001.mp4"
        self.video.write_bytes(b"fake-mp4")
        (self.root / "assets/pro/media").mkdir(parents=True)
        (self.root / "content/pro/rights").mkdir(parents=True)
        media = self.root / "assets/pro/media/bg.mp4"
        media.write_bytes(b"approved-background")
        digest = hashlib.sha256(media.read_bytes()).hexdigest()
        record = {
            "schema_version": 1, "asset_id": "bg-001", "media_type": "visual",
            "file_path": "assets/pro/media/bg.mp4", "file_sha256": digest,
            "source_page_url": "https://example.org/source", "creator_or_performer": "Creator",
            "rights_owner": "Rights owner", "source_platform": "Example stock",
            "downloaded_at": "2026-01-01T00:00:00Z", "license_name": "Example license",
            "license_evidence": {"kind": "url", "value": "https://example.org/license"},
            "intended_uses": {"download": True, "editing": True, "video_synchronization": True,
                "private_review_delivery": True, "public_social_posting": True,
                "commercial_monetized_use": True},
            "territories": ["worldwide"], "validity": {"start": "2025-01-01", "end": None},
            "attribution": {"required": False},
            "third_party_review": {key: {"reviewed": True, "resolved": True}
                for key in ("people", "logos_trademarks", "artwork", "property_privacy", "endorsement")},
            "reviewer": "Human reviewer", "reviewed_at": "2026-01-02T00:00:00Z",
            "decision": "approved",
        }
        (self.root / "content/pro/rights/bg-001.json").write_text(
            json.dumps(record), encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def call_cycle(self, persist, send):
        return run_preview_cycle(
            Path("content/pro/candidate.json"),
            Path("output/pro_preview/PREVIEW-ONLY-dua-candidate-001.mp4"),
            repo_root=self.root, workflow_run_id="run-1", token="fake-token",
            chat_id="12345", branch="feature/quran-video-pro",
            persist_fn=persist, send_fn=send, verify_chat_fn=lambda token, chat_id: None)

    def test_success_persists_reservation_before_one_send_and_final_state(self):
        calls = []
        def persist(root):
            calls.append("persist")
            return True
        def send(*args, **kwargs):
            calls.append("send")
            return {"message_id": 77}
        result = self.call_cycle(persist, send)
        self.assertEqual(calls, ["persist", "send", "persist"])
        self.assertEqual(result["state"], "delivered")
        self.assertFalse(result["tiktok_published"])

    def test_initial_persistence_failure_prevents_telegram(self):
        calls = []
        def persist(root):
            calls.append("persist")
            return False
        def send(*args, **kwargs):
            calls.append("send")
            return {"message_id": 77}
        with self.assertRaisesRegex(RuntimeError, "not confirmed persisted"):
            self.call_cycle(persist, send)
        self.assertEqual(calls, ["persist"])

    def test_ambiguous_sender_failure_marks_uncertain_and_never_retries(self):
        calls = []
        def persist(root):
            calls.append("persist")
            return True
        def send(*args, **kwargs):
            calls.append("send")
            raise TimeoutError("ambiguous")
        with self.assertRaises(TimeoutError):
            self.call_cycle(persist, send)
        self.assertEqual(calls, ["persist", "send", "persist"])
        data = json.loads((self.root / "data/pro_preview_send_ledger.json").read_text())
        self.assertEqual(data["entries"]["candidate-001"]["state"], "uncertain")


    def test_input_changed_after_reservation_is_not_sent(self):
        calls = []
        def persist(root):
            calls.append("persist")
            if len(calls) == 1:
                self.manifest.write_text(self.manifest.read_text() + " ", encoding="utf-8")
            return True
        def send(*args, **kwargs):
            calls.append("send")
            return {"message_id": 77}
        with self.assertRaisesRegex(RuntimeError, "changed after reservation"):
            self.call_cycle(persist, send)
        self.assertEqual(calls, ["persist"])
        data = json.loads((self.root / "data/pro_preview_send_ledger.json").read_text())
        self.assertEqual(data["entries"]["candidate-001"]["state"], "reserved")


    def test_final_persistence_failure_keeps_reserved_remote_boundary(self):
        calls = []
        def persist(root):
            calls.append("persist")
            return len(calls) == 1
        def send(*args, **kwargs):
            calls.append("send")
            return {"message_id": 77}
        with self.assertRaisesRegex(RuntimeError, "final ledger persistence failed"):
            self.call_cycle(persist, send)
        self.assertEqual(calls, ["persist", "send", "persist"])
        data = json.loads((self.root / "data/pro_preview_send_ledger.json").read_text())
        self.assertEqual(data["entries"]["candidate-001"]["state"], "delivered")
        # The first successful persistence happened while the remote state was reserved.

    def test_wrong_branch_prevents_preflight_and_send(self):
        with self.assertRaisesRegex(RuntimeError, "restricted"):
            run_preview_cycle(Path("missing.json"), Path("missing.mp4"), repo_root=self.root,
                workflow_run_id="run", token="t", chat_id="123", branch="main")


    def test_private_chat_verification_failure_prevents_reservation_and_send(self):
        calls = []
        def persist(root):
            calls.append("persist")
            return True
        def send(*args, **kwargs):
            calls.append("send")
            return {"message_id": 77}
        def reject_chat(token, chat_id):
            calls.append("verify")
            raise RuntimeError("not private")
        with self.assertRaisesRegex(RuntimeError, "not private"):
            run_preview_cycle(Path("content/pro/candidate.json"),
                Path("output/pro_preview/PREVIEW-ONLY-dua-candidate-001.mp4"),
                repo_root=self.root, workflow_run_id="run-1", token="fake-token",
                chat_id="12345", branch="feature/quran-video-pro",
                persist_fn=persist, send_fn=send, verify_chat_fn=reject_chat)
        self.assertEqual(calls, ["verify"])
        self.assertFalse((self.root / "data/pro_preview_send_ledger.json").exists())


if __name__ == "__main__":
    unittest.main()
