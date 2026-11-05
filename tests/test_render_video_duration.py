"""Duration safety tests for the Quran renderer."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from render_video_scenes import validate_video_duration, validate_quran_audio_approval


class VideoDurationTests(unittest.TestCase):
    def test_exactly_40_seconds_is_allowed(self):
        validate_video_duration(40.0)

    def test_shorter_than_limit_is_allowed(self):
        validate_video_duration(39.5)

    def test_over_40_seconds_is_rejected(self):
        with self.assertRaisesRegex(SystemExit, "40-second maximum"):
            validate_video_duration(40.001)

    def test_approved_reviewed_recording_passes(self):
        validate_quran_audio_approval({"approved": True, "exact_recording_user_reviewed": True, "rights_verified": True})

    def test_rights_cleared_preview_only_recording_passes_without_user_approval(self):
        validate_quran_audio_approval({"approved": False, "preview_only": True, "exact_recording_user_reviewed": False, "rights_verified": True})

    def test_unapproved_recording_without_preview_flag_is_rejected(self):
        with self.assertRaisesRegex(SystemExit, "not marked approved"):
            validate_quran_audio_approval({"approved": False, "exact_recording_user_reviewed": False, "rights_verified": True})

    def test_preview_only_recording_cannot_be_production_approved(self):
        with self.assertRaisesRegex(SystemExit, "cannot be marked production-approved"):
            validate_quran_audio_approval({"approved": True, "preview_only": True, "rights_verified": True})

    def test_preview_only_recording_still_requires_rights(self):
        with self.assertRaisesRegex(SystemExit, "Reuse permission"):
            validate_quran_audio_approval({"approved": False, "preview_only": True, "rights_verified": False})

    def test_zero_or_negative_duration_is_rejected(self):
        for duration in (0, -1):
            with self.subTest(duration=duration):
                with self.assertRaisesRegex(SystemExit, "must be positive"):
                    validate_video_duration(duration)


if __name__ == "__main__":
    unittest.main()
