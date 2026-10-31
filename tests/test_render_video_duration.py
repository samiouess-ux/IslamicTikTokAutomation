"""Duration safety tests for the Quran renderer."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from render_video_scenes import validate_video_duration


class VideoDurationTests(unittest.TestCase):
    def test_exactly_65_seconds_is_allowed(self):
        validate_video_duration(65.0)

    def test_shorter_than_limit_is_allowed(self):
        validate_video_duration(42.5)

    def test_over_65_seconds_is_rejected(self):
        with self.assertRaisesRegex(SystemExit, "65-second maximum"):
            validate_video_duration(65.001)

    def test_zero_or_negative_duration_is_rejected(self):
        for duration in (0, -1):
            with self.subTest(duration=duration):
                with self.assertRaisesRegex(SystemExit, "must be positive"):
                    validate_video_duration(duration)


if __name__ == "__main__":
    unittest.main()
