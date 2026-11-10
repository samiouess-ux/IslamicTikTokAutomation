"""Unit tests for the production background-reel builder."""
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

    def test_builds_reel_from_multiple_clips_and_checks_final_duration(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            destination = work / "background.mp4"

            def fake_download(url, path):
                path.write_bytes(b"mock video")

            def fake_run(command):
                if "-f" in command and "concat" in command:
                    Path(command[-1]).write_bytes(b"mock reel")

            with patch("render_video_scenes.download", side_effect=fake_download), \
                 patch("render_video_scenes.probe_media_duration", side_effect=[6.0, 5.0, 11.0]), \
                 patch("render_video_scenes.run", side_effect=fake_run) as run:
                build_background_reel(
                    [self._candidate("clip-a"), self._candidate("clip-b")],
                    10.0, work, destination
                )

            self.assertTrue(destination.is_file())
            self.assertEqual(run.call_count, 3)

    def test_rejects_final_reel_shorter_than_audio(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            destination = work / "background.mp4"

            def fake_download(url, path):
                path.write_bytes(b"mock video")

            def fake_run(command):
                if "-f" in command and "concat" in command:
                    Path(command[-1]).write_bytes(b"mock reel")

            with patch("render_video_scenes.download", side_effect=fake_download), \
                 patch("render_video_scenes.probe_media_duration", side_effect=[10.0, 9.8]), \
                 patch("render_video_scenes.run", side_effect=fake_run):
                with self.assertRaisesRegex(SystemExit, "too short"):
                    build_background_reel([self._candidate("clip-a")], 10.0, work, destination)


if __name__ == "__main__":
    unittest.main()
