"""Unit tests for the production background-reel builder."""
import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from render_video_scenes import build_background_reel


class BackgroundReelTests(unittest.TestCase):
    def _candidate(self, name):
        return {
            "id": name,
            "direct_video_url": f"https://cdn.example/{name}.mp4",
        }

    def test_uses_one_long_enough_clip_and_skips_short_candidates(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            destination = work / "background.mp4"

            def fake_download(url, path):
                path.write_bytes(b"mock video")

            def fake_run(command):
                Path(command[-1]).write_bytes(b"mock output")

            with (
                patch("render_video_scenes.download", side_effect=fake_download),
                patch("render_video_scenes.probe_media_duration", side_effect=[6.0, 11.0, 10.0]),
                patch("render_video_scenes.run", side_effect=fake_run) as run,
            ):
                selected = build_background_reel(
                    [self._candidate("clip-a"), self._candidate("clip-b")],
                    10.0, work, destination
                )

            self.assertEqual(selected, "clip-b")
            self.assertTrue(destination.is_file())
            self.assertEqual(run.call_count, 1)
            self.assertEqual(
                run.call_args.args[0][run.call_args.args[0].index("-t") + 1],
                "10.000000",
            )
            self.assertFalse((work / "background_concat.txt").exists())

    def test_rejects_empty_candidate_list(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            with self.assertRaisesRegex(SystemExit, "No approved backgrounds"):
                build_background_reel([], 10.0, work, work / "background.mp4")

    def test_rejects_candidates_with_no_usable_duration(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            destination = work / "background.mp4"

            def fake_download(url, path):
                path.write_bytes(b"mock video")

            with patch("render_video_scenes.download", side_effect=fake_download), \
                 patch("render_video_scenes.probe_media_duration", return_value=0.0), \
                 patch("render_video_scenes.run") as run:
                with self.assertRaisesRegex(SystemExit, "No single approved background"):
                    build_background_reel(
                        [self._candidate("empty-clip")], 10.0, work, destination
                    )
            run.assert_not_called()

    def test_rejects_non_finite_or_non_positive_target_duration(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            for duration in (0.0, -1.0, math.nan, math.inf, -math.inf):
                with self.subTest(duration=duration):
                    with self.assertRaisesRegex(SystemExit, "finite positive"):
                        build_background_reel([], duration, work, work / "background.mp4")

    def test_rejects_final_reel_shorter_than_audio(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            destination = work / "background.mp4"

            def fake_download(url, path):
                path.write_bytes(b"mock video")

            def fake_run(command):
                Path(command[-1]).write_bytes(b"mock output")

            with patch("render_video_scenes.download", side_effect=fake_download), \
                 patch("render_video_scenes.probe_media_duration", side_effect=[9.8]), \
                 patch("render_video_scenes.run", side_effect=fake_run):
                with self.assertRaisesRegex(SystemExit, "No single approved background"):
                    build_background_reel([self._candidate("clip-a")], 10.0, work, destination)


if __name__ == "__main__":
    unittest.main()
