"""Regression tests for background source normalization and validation."""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from render_video_scenes import build_background_reel, probe_background_media


class BackgroundMediaProbeTests(unittest.TestCase):
    def _probe(self, width, height, duration=12.5):
        payload = {
            "streams": [{"codec_type": "video", "width": width, "height": height}],
            "format": {"duration": str(duration)},
        }
        return json.dumps(payload)

    def test_verified_landscape_source_is_accepted_for_center_crop(self):
        with tempfile.TemporaryDirectory() as tmp:
            media = Path(tmp) / "landscape.mp4"
            media.write_bytes(b"mock video")
            with patch(
                "render_video_scenes.subprocess.check_output",
                return_value=self._probe(1920, 1080),
            ):
                self.assertEqual(probe_background_media(media), 12.5)

    def test_verified_portrait_source_is_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            media = Path(tmp) / "portrait.mp4"
            media.write_bytes(b"mock video")
            with patch(
                "render_video_scenes.subprocess.check_output",
                return_value=self._probe(1080, 1920),
            ):
                self.assertEqual(probe_background_media(media), 12.5)

    def test_zero_dimension_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            media = Path(tmp) / "invalid.mp4"
            media.write_bytes(b"mock video")
            with patch(
                "render_video_scenes.subprocess.check_output",
                return_value=self._probe(0, 1080),
            ):
                with self.assertRaisesRegex(SystemExit, "dimensions must be positive"):
                    probe_background_media(media)

    def test_reel_normalizes_landscape_source_to_vertical_canvas(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            destination = work / "background.mp4"
            commands = []

            def fake_download(url, path):
                path.write_bytes(b"mock source")

            def fake_run(command):
                commands.append(command)
                Path(command[-1]).write_bytes(b"mock output")

            with patch("render_video_scenes.download", side_effect=fake_download), patch(
                "render_video_scenes.probe_background_media", return_value=8.0
            ), patch("render_video_scenes.run", side_effect=fake_run), patch(
                "render_video_scenes.validate_rendered_video"
            ):
                build_background_reel(
                    [{"id": "landscape", "direct_video_url": "https://cdn.example/landscape.mp4"}],
                    5.0, work, destination,
                )

            normalize = commands[0]
            vf = normalize[normalize.index("-vf") + 1]
            self.assertIn("scale=1080:1920:force_original_aspect_ratio=increase", vf)
            self.assertIn("crop=1080:1920", vf)
            self.assertIn("setsar=1,fps=30", vf)
            self.assertEqual(commands[-1][-1], str(destination))


if __name__ == "__main__":
    unittest.main()
