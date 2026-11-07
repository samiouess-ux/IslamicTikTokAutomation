"""Regression tests for content-type-specific safety gates."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from validate_content_manifest import validate_content_manifest


class ContentManifestTests(unittest.TestCase):
    def test_existing_quran_manifest_remains_compatible(self):
        data = json.loads((ROOT / "content/first_video.json").read_text(encoding="utf-8"))
        validate_content_manifest(data)

    def test_unapproved_quran_audio_is_allowed_only_as_review_preview(self):
        data = json.loads((ROOT / "content/second_video_ash_sharh_94_1_8_draft.json").read_text(encoding="utf-8"))
        self.assertFalse(data["audio"]["approved"])
        self.assertTrue(data["audio"]["preview_only"])
        self.assertFalse(data["audio"]["exact_recording_user_reviewed"])
        validate_content_manifest(data)

    def test_preview_only_quran_audio_still_requires_reuse_rights(self):
        data = json.loads((ROOT / "content/second_video_ash_sharh_94_1_8_draft.json").read_text(encoding="utf-8"))
        data["audio"]["rights_verified"] = False
        with self.assertRaisesRegex(SystemExit, "Reuse permission"):
            validate_content_manifest(data)

    def test_unapproved_quran_audio_without_preview_gate_is_rejected(self):
        data = json.loads((ROOT / "content/second_video_ash_sharh_94_1_8_draft.json").read_text(encoding="utf-8"))
        data["audio"]["preview_only"] = False
        with self.assertRaisesRegex(SystemExit, "only an explicit preview_only"):
            validate_content_manifest(data)

    def test_preview_only_quran_audio_cannot_be_marked_production_approved(self):
        data = json.loads((ROOT / "content/second_video_ash_sharh_94_1_8_draft.json").read_text(encoding="utf-8"))
        data["audio"]["approved"] = True
        with self.assertRaisesRegex(SystemExit, "cannot also be marked"):
            validate_content_manifest(data)

    def dua_manifest(self):
        return {
            "content_type": "dua",
            "source": {"collection": "review_pending"},
            "items": [{
                "id": "test-dua-001",
                "kind": "quranic_dua",
                "arabic": "نص دعاء تجريبي غير مخصص للإنتاج",
                "source_name": "Test source",
                "source_url": "https://example.org/test",
                "source_reference": "Test reference 1",
                "verification_status": "verified",
                "human_reviewed": True
            }],
            "audio": {
                "kind": "ambient_nature", "approved": True,
                "rights_verified": True, "user_approved": True,
                "music_allowed": False
            },
            "visual": {
                "template": "ornate_gold_classic",
                "background_candidate": {
                    "source_url": "https://example.org/background",
                    "direct_video_url": "https://example.org/background.mp4",
                    "approved": True, "user_approved": True
                }
            },
            "publishing": {"approval_required": True, "auto_publish": False}
        }

    def test_sourced_dua_with_approved_ambient_audio_passes(self):
        validate_content_manifest(self.dua_manifest())

    def test_dua_source_requires_a_real_https_host_and_string_name(self):
        invalid_urls = ("https://", "https:///path", "http://example.org",
                        "https://[invalid-ipv6", 17, None)
        for value in invalid_urls:
            with self.subTest(source_url=value):
                data = self.dua_manifest()
                data["items"][0]["source_url"] = value
                with self.assertRaisesRegex(SystemExit, "valid host"):
                    validate_content_manifest(data)
        for value in (None, 17, ["Trusted source"], ""):
            with self.subTest(source_name=value):
                data = self.dua_manifest()
                data["items"][0]["source_name"] = value
                with self.assertRaisesRegex(SystemExit, "named HTTPS religious source"):
                    validate_content_manifest(data)

    def test_dua_without_source_is_rejected(self):
        data = self.dua_manifest()
        data["items"][0]["source_url"] = ""
        with self.assertRaisesRegex(SystemExit, "HTTPS religious source"):
            validate_content_manifest(data)

    def test_dua_without_human_review_is_rejected(self):
        data = self.dua_manifest()
        data["items"][0]["human_reviewed"] = False
        with self.assertRaisesRegex(SystemExit, "explicit human review"):
            validate_content_manifest(data)

    def test_candidate_preview_allows_pending_human_review_only_on_explicit_path(self):
        data = self.dua_manifest()
        data["lifecycle_status"] = "candidate_preview"
        data["preview_only"] = True
        data["rotation_approved"] = False
        data["items"][0]["human_reviewed"] = False
        with self.assertRaisesRegex(SystemExit, "explicit preview-only"):
            validate_content_manifest(data)
        validate_content_manifest(data, allow_candidate_preview=True)

    def test_candidate_preview_cannot_be_promoted_by_preview_flag_alone(self):
        data = self.dua_manifest()
        data["lifecycle_status"] = "candidate_preview"
        data["preview_only"] = True
        data["items"][0]["human_reviewed"] = False
        with self.assertRaisesRegex(SystemExit, "explicit preview-only"):
            validate_content_manifest(data)
        with self.assertRaisesRegex(SystemExit, "cannot be marked production-approved"):
            data["lifecycle_status"] = "production_approved"
            validate_content_manifest(data, allow_candidate_preview=True)

    def test_production_approved_manifest_still_requires_human_review(self):
        data = self.dua_manifest()
        data["lifecycle_status"] = "production_approved"
        data["items"][0]["human_reviewed"] = False
        with self.assertRaisesRegex(SystemExit, "explicit human review"):
            validate_content_manifest(data)

    def test_prophetic_dua_requires_hadith_grading(self):
        data = self.dua_manifest()
        data["items"][0]["kind"] = "prophetic_dua"
        with self.assertRaisesRegex(SystemExit, "hadith grading"):
            validate_content_manifest(data)

    def test_duplicate_item_ids_are_rejected(self):
        data = self.dua_manifest()
        data["items"].append(dict(data["items"][0]))
        with self.assertRaisesRegex(SystemExit, "unique, stable id"):
            validate_content_manifest(data)

    def test_dua_cannot_use_quran_recitation_audio_kind(self):
        data = self.dua_manifest()
        data["audio"]["kind"] = "quran_recitation"
        with self.assertRaisesRegex(SystemExit, "must not be mislabeled"):
            validate_content_manifest(data)

    def test_unapproved_background_is_rejected(self):
        data = self.dua_manifest()
        data["visual"]["background_candidate"]["user_approved"] = False
        with self.assertRaisesRegex(SystemExit, "Background must be approved"):
            validate_content_manifest(data)

    def test_enum_fields_reject_unhashable_json_values(self):
        cases = [
            ("content_type", ["dua"]),
            ("visual", ["template"], ["ornate_gold_classic"]),
            ("audio", ["kind"], ["ambient_nature"]),
            ("item", ["kind"], ["quranic_dua"]),
        ]
        for case in cases:
            with self.subTest(case=case[0]):
                data = self.dua_manifest()
                if case[0] == "content_type":
                    data["content_type"] = case[1]
                elif case[0] == "visual":
                    data["visual"]["template"] = case[2]
                elif case[0] == "audio":
                    data["audio"]["kind"] = case[2]
                else:
                    data["items"][0]["kind"] = case[2]
                with self.assertRaises(SystemExit):
                    validate_content_manifest(data)

    def test_repeat_count_rejects_boolean_values(self):
        for invalid in (True, False):
            with self.subTest(repeat_count=invalid):
                data = self.dua_manifest()
                data["items"][0]["repeat_count"] = invalid
                with self.assertRaisesRegex(SystemExit, "repeat_count must be a positive integer"):
                    validate_content_manifest(data)

    def test_audio_approval_flags_require_literal_true(self):
        for field in ("approved", "rights_verified", "user_approved"):
            with self.subTest(field=field):
                data = self.dua_manifest()
                data["audio"][field] = "false"
                with self.assertRaisesRegex(SystemExit, "explicit approval"):
                    validate_content_manifest(data)

    def test_spoken_dua_review_flag_requires_literal_true(self):
        data = self.dua_manifest()
        data["audio"]["kind"] = "spoken_dua"
        data["audio"]["exact_recording_user_reviewed"] = "false"
        with self.assertRaisesRegex(SystemExit, "must be user-reviewed"):
            validate_content_manifest(data)

    def test_quran_license_candidates_must_be_a_list(self):
        data = json.loads((ROOT / "content/first_video.json").read_text(encoding="utf-8"))
        data["audio"]["rights_verified"] = False
        data["audio"]["license_research_candidates"] = {"status": "approved_test"}
        with self.assertRaisesRegex(SystemExit, "must be a list"):
            validate_content_manifest(data)

    def test_quran_license_candidate_status_must_be_a_string(self):
        data = json.loads((ROOT / "content/first_video.json").read_text(encoding="utf-8"))
        data["audio"]["rights_verified"] = False
        data["audio"]["license_research_candidates"] = [{"status": ["approved_test"]}]
        with self.assertRaisesRegex(SystemExit, "Reuse permission"):
            validate_content_manifest(data)

    def test_quran_recording_review_flags_require_literal_true(self):
        for placement in ("audio", "candidate"):
            with self.subTest(placement=placement):
                data = json.loads((ROOT / "content/first_video.json").read_text(encoding="utf-8"))
                candidate = data["audio"]["license_research_candidates"][0]
                candidate["exact_recording_user_reviewed"] = False
                if placement == "audio":
                    data["audio"]["exact_recording_user_reviewed"] = "false"
                else:
                    candidate["exact_recording_user_reviewed"] = "false"
                with self.assertRaisesRegex(SystemExit, "has not been user-reviewed"):
                    validate_content_manifest(data)

    def test_quran_license_candidates_shape_is_checked_before_review_scan(self):
        data = json.loads((ROOT / "content/first_video.json").read_text(encoding="utf-8"))
        data["audio"]["license_research_candidates"] = None
        with self.assertRaisesRegex(SystemExit, "must be a list"):
            validate_content_manifest(data)

    def test_auto_publish_is_always_rejected(self):
        data = self.dua_manifest()
        data["publishing"]["auto_publish"] = True
        with self.assertRaisesRegex(SystemExit, "Auto-publishing"):
            validate_content_manifest(data)


if __name__ == "__main__":
    unittest.main()
