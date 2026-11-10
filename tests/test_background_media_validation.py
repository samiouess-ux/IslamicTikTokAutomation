"""Tests for fail-closed validation of downloaded background media."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from render_video_scenes import probe_background_media


class BackgroundMediaValidationTests(unittest.TestCase):
    def _probe(self, streams, duration="12.5"):
        return json.dumps({
            "streams": streams,
            "format": {"duration": duration},
        })

    def test_accepts_nonempty_portrait_video_and_returns_probed_duration(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "background.mp4"
            path.write_bytes(b"video")
            payload = self._probe([{
                "codec_type": "video", "width": 1080, "height": 1920,
            }])
            with patch("render_video_scenes.subprocess.check_output", return_value=payload):
                self.assertEqual(probe_background_media(path), 12.5)

    def test_rejects_media_without_video_stream(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "audio.mp4"
            path.write_bytes(b"not-empty")
            payload = self._probe([{"codec_type": "audio"}])
            with patch("render_video_scenes.subprocess.check_output", return_value=payload):
                with self.assertRaisesRegex(SystemExit, "not a readable video"):
                    probe_background_media(path)

    def test_rejects_landscape_video(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "landscape.mp4"
            path.write_bytes(b"video")
            payload = self._probe([{
                "codec_type": "video", "width": 1920, "height": 1080,
            }])
            with patch("render_video_scenes.subprocess.check_output", return_value=payload):
                with self.assertRaisesRegex(SystemExit, "portrait 9:16"):
                    probe_background_media(path)

    def test_rejects_empty_download_before_probing(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "empty.mp4"
            path.touch()
            with patch("render_video_scenes.subprocess.check_output") as probe:
                with self.assertRaisesRegex(SystemExit, "missing or empty"):
                    probe_background_media(path)
            probe.assert_not_called()

    def test_rejects_nonfinite_duration(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "background.mp4"
            path.write_bytes(b"video")
            payload = self._probe([{
                "codec_type": "video", "width": 1080, "height": 1920,
            }], duration="NaN")
            with patch("render_video_scenes.subprocess.check_output", return_value=payload):
                with self.assertRaisesRegex(SystemExit, "Invalid background duration"):
                    probe_background_media(path)


if __name__ == "__main__":
    unittest.main()
