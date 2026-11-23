"""Tests for mixed, reviewable photo/video background selection and rendering."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from background_mixed_renderer import (
    build_mixed_background_reel,
    select_scene_backgrounds,
)


class MixedBackgroundRendererTests(unittest.TestCase):
    def _assets(self, root: Path):
        photo = root / "photo.jpg"
        Image.effect_noise((900, 1600), 100).convert("RGB").save(photo, quality=95)
        video = root / "video.mp4"
        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-f", "lavfi", "-i", "color=c=blue:s=360x640:r=30:d=2",
            "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(video)
        ], check=True)
        return [
            {"media_type": "photo", "asset_id": "photo-1", "asset_path": str(photo)},
            {"media_type": "video", "asset_id": "video-1",
             "asset_url": video.as_uri().replace("file://", "https://invalid.example/")},
        ], video

    def test_selector_is_deterministic_and_alternates_media_when_possible(self):
        assets = [
            {"media_type": "photo", "asset_id": "p1"},
            {"media_type": "photo", "asset_id": "p2"},
            {"media_type": "video", "asset_id": "v1"},
            {"media_type": "video", "asset_id": "v2"},
        ]
        first = select_scene_backgrounds(assets, 4, "stable-key")
        second = select_scene_backgrounds(assets, 4, "stable-key")
        self.assertEqual([x["asset_id"] for x in first], [x["asset_id"] for x in second])
        self.assertTrue(all(first[i]["media_type"] != first[i-1]["media_type"] for i in range(1, 4)))

    def test_rejects_empty_assets_and_duplicate_ids(self):
        with self.assertRaisesRegex(ValueError, "No approved"):
            select_scene_backgrounds([], 1, "key")
        with self.assertRaisesRegex(ValueError, "unique"):
            select_scene_backgrounds([
                {"media_type": "photo", "asset_id": "same"},
                {"media_type": "video", "asset_id": "same"},
            ], 1, "key")

    def test_renders_photo_and_video_scenes_into_one_portrait_reel(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            assets, source_video = self._assets(root)
            assets[1]["asset_url"] = "https://invalid.example/not-used.mp4"
            # Exercise the video branch without a network dependency by patching
            # the downloader to copy the local fixture into its requested path.
            import background_mixed_renderer as renderer
            original_download = renderer._download
            renderer._download = lambda _url, destination: destination.write_bytes(source_video.read_bytes())
            try:
                output = root / "mixed.mp4"
                ids = build_mixed_background_reel(
                    assets,
                    [{"duration": 0.8}, {"duration": 0.8}],
                    1.6,
                    root / "work",
                    output,
                    "mixed-test-key",
                )
            finally:
                renderer._download = original_download

            self.assertEqual(len(ids), 2)
            self.assertTrue(output.is_file())
            probe = subprocess.check_output([
                "ffprobe", "-v", "error", "-select_streams", "v:0",
                "-show_entries", "stream=width,height:format=duration",
                "-of", "default=noprint_wrappers=1", str(output)
            ], text=True)
            self.assertIn("width=1080", probe)
            self.assertIn("height=1920", probe)
            self.assertIn("duration=", probe)


if __name__ == "__main__":
    unittest.main()
