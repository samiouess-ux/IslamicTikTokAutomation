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


if __name__ == "__main__":
    unittest.main()
