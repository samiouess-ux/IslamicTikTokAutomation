"""Offline tests for per-asset media rights evidence and hash binding."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from validate_pro_media_rights import validate_manifest_media_rights


def base_record(asset_id="visual-001", media_type="visual", file_path="assets/pro/media/visual.mp4",
                digest=None):
    return {
        "schema_version": 1, "asset_id": asset_id, "media_type": media_type,
        "file_path": file_path, "file_sha256": digest,
        "source_page_url": "https://stock.example/assets/visual-001",
        "creator_or_performer": "Creator", "rights_owner": "Rights owner",
        "source_platform": "Example Stock", "downloaded_at": "2026-01-01T00:00:00Z",
        "license_name": "Individual asset commercial license",
        "license_evidence": {"kind": "url", "value": "https://stock.example/legal/license"},
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


class MediaRightsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "assets/pro/media").mkdir(parents=True)
        (self.root / "content/pro/rights").mkdir(parents=True)
        self.asset = self.root / "assets/pro/media/visual.mp4"
        self.asset.write_bytes(b"approved-visual")
        self.record = base_record(digest=hashlib.sha256(self.asset.read_bytes()).hexdigest())
        (self.root / "content/pro/rights/visual-001.json").write_text(
            json.dumps(self.record), encoding="utf-8")
        self.manifest = {
            "media_assets": [{"asset_id": "visual-001", "media_type": "visual"}],
            "visual": {"background_candidate": {"asset_id": "visual-001",
                "source_url": self.record["source_page_url"]}},
            "audio": {"kind": "silent"},
        }

    def tearDown(self):
        self.tmp.cleanup()

    def save(self):
        (self.root / "content/pro/rights/visual-001.json").write_text(
            json.dumps(self.record), encoding="utf-8")

    def validate(self):
        return validate_manifest_media_rights(self.manifest, repo_root=self.root)

    def test_valid_visual_and_silent_audio_pass(self):
        result = self.validate()
        self.assertEqual(result["visual"], self.asset)

    def test_missing_rights_record_fails_closed(self):
        (self.root / "content/pro/rights/visual-001.json").unlink()
        with self.assertRaisesRegex(ValueError, "record is missing"):
            self.validate()

    def test_file_hash_mismatch_fails_closed(self):
        self.asset.write_bytes(b"changed-bytes")
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            self.validate()

    def test_manifest_asset_reference_mismatch_fails_closed(self):
        self.manifest["visual"]["background_candidate"]["asset_id"] = "other-id"
        with self.assertRaisesRegex(ValueError, "references do not exactly match"):
            self.validate()

    def test_missing_public_posting_or_commercial_scope_fails_closed(self):
        self.record["intended_uses"]["public_social_posting"] = False
        self.save()
        with self.assertRaisesRegex(ValueError, "public_social_posting"):
            self.validate()
        self.record["intended_uses"]["public_social_posting"] = True
        self.record["intended_uses"]["commercial_monetized_use"] = False
        self.save()
        with self.assertRaisesRegex(ValueError, "commercial_monetized_use"):
            self.validate()

    def test_expired_permission_fails_closed(self):
        self.record["validity"]["end"] = "2020-01-01"
        self.save()
        with self.assertRaisesRegex(ValueError, "expired"):
            self.validate()

    def test_unresolved_third_party_issue_fails_closed(self):
        self.record["third_party_review"]["logos_trademarks"]["resolved"] = False
        self.save()
        with self.assertRaisesRegex(ValueError, "unresolved"):
            self.validate()

    def test_generic_root_source_page_is_not_asset_specific(self):
        self.record["source_page_url"] = "https://stock.example/"
        self.manifest["visual"]["background_candidate"]["source_url"] = "https://stock.example/"
        self.save()
        with self.assertRaisesRegex(ValueError, "exact HTTPS URL"):
            self.validate()


    def test_required_attribution_is_blocked_until_renderer_supports_it(self):
        self.record["attribution"] = {"required": True, "text": "Credit Creator"}
        self.save()
        with self.assertRaisesRegex(ValueError, "attribution is not yet injected"):
            self.validate()

    def test_audio_requires_performer_recording_owner_and_asset_record(self):
        audio = self.root / "assets/pro/media/voice.mp3"
        audio.write_bytes(b"recording")
        digest = hashlib.sha256(audio.read_bytes()).hexdigest()
        record = base_record("audio-001", "audio", "assets/pro/media/voice.mp3", digest)
        record["performer"] = "Named performer"
        record["recording_owner"] = "Recording owner"
        (self.root / "content/pro/rights/audio-001.json").write_text(json.dumps(record), encoding="utf-8")
        self.manifest["audio"] = {"kind": "spoken_dua", "asset_id": "audio-001"}
        self.manifest["media_assets"].append({"asset_id": "audio-001", "media_type": "audio"})
        result = self.validate()
        self.assertEqual(result["audio"], audio)
        record.pop("recording_owner")
        (self.root / "content/pro/rights/audio-001.json").write_text(json.dumps(record), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "recording owner"):
            self.validate()


if __name__ == "__main__":
    unittest.main()
