"""Regression tests for verse-screen timing against the actual audio duration."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from render_video_scenes import calculate_scene_boundaries


class SceneTimingTests(unittest.TestCase):
    def setUp(self):
        self.scenes = [
            {"scene": 1, "verses": [5]},
            {"scene": 2, "verses": [6]},
        ]

    def test_uses_processed_verse_durations_and_real_inter_verse_gap(self):
        boundaries = calculate_scene_boundaries(
            self.scenes, {5: 3.25, 6: 4.10}, 0.02, 7.39
        )
        self.assertEqual(boundaries, [3.27])

    def test_rejects_non_finite_or_non_positive_verse_duration(self):
        for invalid in (0.0, -1.0, float("nan"), float("inf")):
            with self.subTest(duration=invalid):
                with self.assertRaisesRegex(SystemExit, "verse duration"):
                    calculate_scene_boundaries(
                        self.scenes, {5: invalid, 6: 4.0}, 0.0, 8.0
                    )

    def test_rejects_negative_or_non_finite_inter_verse_gap(self):
        for invalid in (-0.01, float("nan"), float("inf")):
            with self.subTest(gap=invalid):
                with self.assertRaisesRegex(SystemExit, "gap"):
                    calculate_scene_boundaries(
                        self.scenes, {5: 3.0, 6: 4.0}, invalid, 8.0
                    )

    def test_rejects_boundary_at_or_beyond_audio_end(self):
        with self.assertRaisesRegex(SystemExit, "at or beyond"):
            calculate_scene_boundaries(
                self.scenes, {5: 8.0, 6: 1.0}, 0.0, 8.0
            )

    def test_rejects_missing_processed_verse_duration(self):
        with self.assertRaisesRegex(SystemExit, "Missing processed duration"):
            calculate_scene_boundaries(
                self.scenes, {5: 3.0}, 0.0, 8.0
            )


if __name__ == "__main__":
    unittest.main()
