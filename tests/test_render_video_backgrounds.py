"""Regression tests for background source normalization and validation."""
import json
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

    def test_source_without_video_stream_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            media = Path(tmp) / "audio-only.mp4"
            media.write_bytes(b"mock media")
            payload = json.dumps({
                "streams": [{"codec_type": "audio"}],
                "format": {"duration": "12.5"},
            })
            with patch(
                "render_video_scenes.subprocess.check_output",
                return_value=payload,
            ):
                with self.assertRaisesRegex(SystemExit, "not a readable video"):
                    probe_background_media(media)

    def test_non_positive_source_duration_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            media = Path(tmp) / "zero-duration.mp4"
            media.write_bytes(b"mock video")
            with patch(
                "render_video_scenes.subprocess.check_output",
                return_value=self._probe(1920, 1080, duration=0),
            ):
                with self.assertRaisesRegex(SystemExit, "Invalid background duration"):
                    probe_background_media(media)

    def test_reel_skips_failed_candidate_and_uses_next_approved_clip(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            destination = work / "background.mp4"
            commands = []

            def fake_download(url, path):
                if "unavailable" in url:
                    raise OSError("source unavailable")
                path.write_bytes(b"mock source")

            def fake_run(command):
                commands.append(command)
                Path(command[-1]).write_bytes(b"mock output")

            candidates = [
                {"id": "unavailable", "direct_video_url": "https://cdn.example/unavailable.mp4"},
                {"id": "usable", "direct_video_url": "https://cdn.example/usable.mp4"},
            ]
            with patch("render_video_scenes.download", side_effect=fake_download), patch(
                "render_video_scenes.probe_background_media", return_value=8.0
            ), patch("render_video_scenes.run", side_effect=fake_run), patch(
                "render_video_scenes.validate_rendered_video"
            ):
                build_background_reel(candidates, 5.0, work, destination)

            self.assertEqual(len(commands), 2)
            self.assertTrue(any(arg.endswith("background_source_0.mp4") for arg in commands[0]))
            self.assertTrue(destination.is_file())

    def test_reel_fails_clearly_when_all_approved_candidates_are_unusable(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            destination = work / "background.mp4"
            candidates = [
                {"id": "bad-a", "direct_video_url": "https://cdn.example/bad-a.mp4"},
                {"id": "bad-b", "direct_video_url": "https://cdn.example/bad-b.mp4"},
            ]
            with patch(
                "render_video_scenes.download", side_effect=OSError("source unavailable")
            ):
                with self.assertRaisesRegex(
                    SystemExit, "No approved background clips could be downloaded and verified"
                ):
                    build_background_reel(candidates, 5.0, work, destination)

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
