"""Tests for fail-closed validation of downloaded background media."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from render_video_scenes import (download, probe_background_media, validate_rendered_video,
                                 validate_final_review_video)


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

    def test_accepts_landscape_video_for_center_crop(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "landscape.mp4"
            path.write_bytes(b"video")
            payload = self._probe([{
                "codec_type": "video", "width": 1920, "height": 1080,
            }])
            with patch("render_video_scenes.subprocess.check_output", return_value=payload):
                self.assertEqual(probe_background_media(path), 12.5)

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


    def test_rejects_generated_file_without_video_stream(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "reel.mp4"
            path.write_bytes(b"video")
            payload = self._probe([{"codec_type": "audio"}])
            with patch("render_video_scenes.subprocess.check_output", return_value=payload):
                with self.assertRaisesRegex(SystemExit, "not a readable video"):
                    validate_rendered_video(path, 10.0)

    def test_rejects_generated_video_with_wrong_dimensions(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "reel.mp4"
            path.write_bytes(b"video")
            payload = self._probe([{"codec_type": "video", "width": 1920, "height": 1080}])
            with patch("render_video_scenes.subprocess.check_output", return_value=payload):
                with self.assertRaisesRegex(SystemExit, "1080x1920"):
                    validate_rendered_video(path, 10.0)

    def test_rejects_generated_video_shorter_than_audio(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "reel.mp4"
            path.write_bytes(b"video")
            payload = self._probe([{"codec_type": "video", "width": 1080, "height": 1920}], duration="8.0")
            with patch("render_video_scenes.subprocess.check_output", return_value=payload):
                with self.assertRaisesRegex(SystemExit, "too short"):
                    validate_rendered_video(path, 10.0)

    def _final_video_payload(self, duration="12.5", audio=True, width=1080, height=1920, fps="30/1"):
        streams = [{
            "codec_type": "video", "width": width, "height": height,
            "avg_frame_rate": fps, "duration": duration,
        }]
        if audio:
            streams.append({"codec_type": "audio", "duration": duration})
        return json.dumps({"streams": streams, "format": {"duration": duration}})

    def test_accepts_valid_final_review_video(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "review.mp4"
            path.write_bytes(b"video")
            with patch("render_video_scenes.subprocess.check_output",
                       return_value=self._final_video_payload()):
                validate_final_review_video(path, 12.4)

    def test_rejects_final_review_video_without_audio(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "review.mp4"
            path.write_bytes(b"video")
            payload = self._final_video_payload(audio=False)
            with patch("render_video_scenes.subprocess.check_output", return_value=payload):
                with self.assertRaisesRegex(SystemExit, "audio/video MP4"):
                    validate_final_review_video(path, 12.4)

    def test_rejects_final_review_video_with_wrong_frame_rate(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "review.mp4"
            path.write_bytes(b"video")
            payload = self._final_video_payload(fps="25/1")
            with patch("render_video_scenes.subprocess.check_output", return_value=payload):
                with self.assertRaisesRegex(SystemExit, "30 fps"):
                    validate_final_review_video(path, 12.4)

    def test_rejects_final_review_video_shorter_than_audio(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "review.mp4"
            path.write_bytes(b"video")
            payload = self._final_video_payload(duration="10.0")
            with patch("render_video_scenes.subprocess.check_output", return_value=payload):
                with self.assertRaisesRegex(SystemExit, "streams do not cover"):
                    validate_final_review_video(path, 12.4)

    def test_rejects_short_video_stream_even_when_container_duration_matches(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "review.mp4"
            path.write_bytes(b"video")
            payload = json.dumps({
                "streams": [
                    {"codec_type": "video", "width": 1080, "height": 1920,
                     "avg_frame_rate": "30/1", "duration": "10.0"},
                    {"codec_type": "audio", "duration": "12.5"},
                ],
                "format": {"duration": "12.5"},
            })
            with patch("render_video_scenes.subprocess.check_output", return_value=payload):
                with self.assertRaisesRegex(SystemExit, "streams do not cover"):
                    validate_final_review_video(path, 12.4)

    def test_download_rejects_oversized_content_length_and_cleans_partial(self):
        class FakeResponse:
            headers = {"Content-Length": str(300 * 1024 * 1024)}
            def __enter__(self): return self
            def __exit__(self, *args): return False

        class FakeOpener:
            def open(self, request, timeout):
                self.request = request
                self.timeout = timeout
                return FakeResponse()

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "partial.mp4"
            path.write_bytes(b"stale partial data")
            opener = FakeOpener()
            with patch("render_video_scenes.urllib.request.build_opener", return_value=opener):
                with self.assertRaisesRegex(SystemExit, "250 MiB"):
                    download("https://videos.pexels.com/video-files/test.mp4", path)
            self.assertEqual(opener.timeout, 90)
            self.assertEqual(
                opener.request.full_url,
                "https://videos.pexels.com/video-files/test.mp4",
            )
            self.assertFalse(path.exists())

if __name__ == "__main__":
    unittest.main()
